import pytest
import asyncio
import time
from typing import List
from omnicore.ir.enums import Capability
from omnicore.optimizer.optimization_context import OptimizedExecutionNode, OptimizedExecutionDAG
from omnicore.cluster.resource import ResourceRequirement, ResourceState
from omnicore.cluster.worker import ClusterWorker, BrokenWorker
from omnicore.communication.message_bus import LocalMessageBus
from omnicore.distributed.cluster_manager import DistributedClusterManager
from omnicore.distributed.exceptions import WorkerNotFoundError, ResourceExhaustedError, ClusterError

# --- Test Helpers ---

@pytest.fixture
def anyio_backend():
    return "asyncio"

def create_execution_dag() -> OptimizedExecutionDAG:
    # 2 nodes: search -> summarize (sequential flow dependencies)
    n1 = OptimizedExecutionNode(
        node_id="search_1",
        name="Search",
        description="Search info",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings"
    )
    n2 = OptimizedExecutionNode(
        node_id="summarize_1",
        name="Summarize",
        description="Summarize findings",
        capability=Capability.SUMMARIZATION,
        input="findings",
        output="summary"
    )
    return OptimizedExecutionDAG(
        nodes=[n1, n2],
        topological_order=["search_1", "summarize_1"]
    )

# --- Integration and Unit Tests ---

@pytest.mark.anyio
async def test_worker_registration_and_heartbeats():
    """Verify registry tracks registrations, heartbeat monitors, and shutdowns."""
    bus = LocalMessageBus()
    manager = DistributedClusterManager(bus)
    await manager.start()

    res = ResourceState(total_cpu_cores=4.0, total_memory_mb=4096.0)
    worker = ClusterWorker(
        worker_id="worker_test_1",
        capabilities=[Capability.WEB_SEARCH, Capability.SUMMARIZATION],
        resources=res,
        bus=bus,
        heartbeat_interval=0.1
    )
    
    # Start worker -> registers with coordinator
    await worker.start()
    
    # Wait for registration callback propagation
    await asyncio.sleep(0.2)
    
    assert "worker_test_1" in manager.registry.list_active_workers()
    
    # Stop worker -> unregisters
    await worker.stop()
    await asyncio.sleep(0.2)
    
    assert "worker_test_1" not in manager.registry.list_active_workers()
    await manager.stop()


@pytest.mark.anyio
async def test_heartbeat_timeout_offline_sweep():
    """Verify monitor sweep identifies silent workers as offline after timeouts."""
    bus = LocalMessageBus()
    # Set short timeout to speed up tests
    manager = DistributedClusterManager(bus)
    manager.heartbeat_monitor.timeout_seconds = 0.2
    await manager.start()

    res = ResourceState(total_cpu_cores=4.0, total_memory_mb=4096.0)
    # Register directly to bypass active heartbeat loop
    manager.register_worker("worker_silent", res, [Capability.WEB_SEARCH])
    
    # Check initially online
    assert "worker_silent" in manager.registry.list_active_workers()
    
    # Wait for timeout sweep (0.2s timeout, wait 0.4s)
    await asyncio.sleep(0.4)
    
    # Check offline status update
    assert "worker_silent" not in manager.registry.list_active_workers()
    await manager.stop()


@pytest.mark.anyio
async def test_load_balancer_policies():
    """Verify LoadBalancer selects workers based on LeastLoaded and ResourceAware policies."""
    manager = DistributedClusterManager()
    
    r1 = ResourceState(total_cpu_cores=4.0, total_memory_mb=4096.0)
    r2 = ResourceState(total_cpu_cores=4.0, total_memory_mb=4096.0)
    
    # 1. Least Loaded test
    manager.register_worker("w1", r1, [Capability.WEB_SEARCH])
    manager.register_worker("w2", r2, [Capability.WEB_SEARCH])
    
    # Set w1 as loaded
    manager.registry.get_worker("w1")["active_tasks"] = 3
    manager.registry.get_worker("w2")["active_tasks"] = 1
    
    req = ResourceRequirement(cpu_cores=1.0, memory_mb=512.0)
    selected = manager.load_balancer.select_worker(Capability.WEB_SEARCH, req, policy="least_loaded")
    # Should choose w2 because active_tasks: 1 < 3
    assert selected == "w2"

    # 2. Resource Aware test
    # Reduce free CPU of w2 by allocating most of it
    manager.registry.get_worker("w2")["resources"].allocated_cpu_cores = 3.5 # free CPU = 0.5
    manager.registry.get_worker("w1")["resources"].allocated_cpu_cores = 1.0 # free CPU = 3.0
    
    selected_res = manager.load_balancer.select_worker(Capability.WEB_SEARCH, req, policy="resource_aware")
    # Should choose w1 because free_cpu: 3.0 > 0.5
    assert selected_res == "w1"


@pytest.mark.anyio
async def test_resource_exhaustion():
    """Verify load balancer raises ResourceExhaustedError on capacity limits."""
    manager = DistributedClusterManager()
    r = ResourceState(total_cpu_cores=1.0, total_memory_mb=512.0)
    manager.register_worker("w1", r, [Capability.WEB_SEARCH])
    
    # Request exceeds CPU cores limit
    req = ResourceRequirement(cpu_cores=2.0, memory_mb=128.0)
    with pytest.raises(ResourceExhaustedError):
        manager.load_balancer.select_worker(Capability.WEB_SEARCH, req, policy="resource_aware")


@pytest.mark.anyio
async def test_distributed_dag_execution():
    """Verify executing complete Execution DAG workflows across workers."""
    bus = LocalMessageBus()
    manager = DistributedClusterManager(bus)
    await manager.start()

    res = ResourceState(total_cpu_cores=4.0, total_memory_mb=4096.0)
    worker1 = ClusterWorker(
        worker_id="w1", capabilities=[Capability.WEB_SEARCH], resources=res, bus=bus
    )
    worker2 = ClusterWorker(
        worker_id="w2", capabilities=[Capability.SUMMARIZATION], resources=res, bus=bus
    )

    await worker1.start()
    await worker2.start()
    await asyncio.sleep(0.2) # registration sync

    dag = create_execution_dag()
    results = await manager.submit(dag, {"query": "deep learning"})
    
    # Check outputs are resolved and passed down the pipeline
    assert "search_1" in results
    assert "summarize_1" in results
    assert "deep learning" in results["summarize_1"]

    await worker1.stop()
    await worker2.stop()
    await manager.stop()


@pytest.mark.anyio
async def test_distributed_fault_recovery_redistribution():
    """Verify fault tolerance manager reschedules tasks on worker timeout failures."""
    bus = LocalMessageBus()
    manager = DistributedClusterManager(bus)
    manager.heartbeat_monitor.timeout_seconds = 0.2
    await manager.start()

    res = ResourceState(total_cpu_cores=4.0, total_memory_mb=4096.0)
    
    # Worker 1 is broken and silent (does not respond to tasks)
    worker1 = BrokenWorker(
        worker_id="broken_w1", capabilities=[Capability.WEB_SEARCH], resources=res, bus=bus, heartbeat_interval=0.05
    )
    # Worker 2 is healthy and online
    worker2 = ClusterWorker(
        worker_id="healthy_w2", capabilities=[Capability.WEB_SEARCH], resources=res, bus=bus, heartbeat_interval=0.05
    )

    await worker1.start()
    await worker2.start()
    await asyncio.sleep(0.2) # registration sync

    # Submit task requiring WEB_SEARCH
    dag = OptimizedExecutionDAG(
        nodes=[OptimizedExecutionNode(
            node_id="n1", name="Task", description="desc", capability=Capability.WEB_SEARCH, input="query", output="findings"
        )],
        topological_order=["n1"]
    )
    
    # Target the broken worker first by making healthy worker loaded
    manager.registry.get_worker("healthy_w2")["active_tasks"] = 5
    
    # Start task. It schedules on broken_w1.
    submit_task = asyncio.create_task(manager.submit(dag, {"query": "ml info"}))
    
    # Wait for scheduling dispatch to broken_w1
    await asyncio.sleep(0.1)
    
    # Shutdown broken worker's heartbeat sending (marks offline via timeout sweep)
    # Simulate worker crash by cancelling heartbeat loop and unsubscribing from tasks without unregistering
    if worker1._heartbeat_task:
        worker1._heartbeat_task.cancel()
    worker1.bus.unsubscribe(f"worker_tasks_{worker1.worker_id}", worker1._receive_task)
    
    # Wait for monitor timeout sweep to detect failure and trigger fault recovery rescheduling
    await asyncio.sleep(0.4)
    
    # Free up healthy worker
    manager.registry.get_worker("healthy_w2")["active_tasks"] = 0
    
    results = await submit_task
    # Should complete successfully because task was reassigned to healthy_w2
    assert "n1" in results
    assert "ml info" in results["n1"]

    await worker2.stop()
    await manager.stop()
