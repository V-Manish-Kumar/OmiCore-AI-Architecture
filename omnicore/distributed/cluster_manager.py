import uuid
from typing import Dict, Any, List, Optional
from omnicore.optimizer.optimization_context import OptimizedExecutionDAG
from omnicore.ir.enums import Capability
from omnicore.cluster.resource import ResourceState
from omnicore.communication.message_bus import LocalMessageBus
from omnicore.distributed.node_registry import NodeRegistry
from omnicore.distributed.resource_manager import ResourceManager
from omnicore.distributed.load_balancer import LoadBalancer
from omnicore.distributed.dispatcher import TaskDispatcher
from omnicore.distributed.fault_tolerance import FaultToleranceManager
from omnicore.distributed.metrics import ClusterMetricsTracker
from omnicore.distributed.diagnostics import ClusterDiagnostics
from omnicore.distributed.autoscaling import Autoscaler
from omnicore.distributed.heartbeat import HeartbeatMonitor
from omnicore.distributed.scheduler import DistributedScheduler
from omnicore.cluster.coordinator import ClusterCoordinator

class DistributedClusterManager:
    """
    Unified Orchestrator and entry point for distributed Execution DAG scheduling.
    Wires up communication, load balancing, registries, metrics, diagnostics,
    health monitors, and scheduler loops.
    """
    def __init__(self, bus: Optional[LocalMessageBus] = None):
        self.bus = bus or LocalMessageBus.get_instance()
        
        # Wires components
        self.registry = NodeRegistry()
        self.coordinator = ClusterCoordinator(self.registry, self.bus)
        self.resource_manager = ResourceManager(self.registry)
        self.load_balancer = LoadBalancer(self.registry)
        self.dispatcher = TaskDispatcher(self.bus, self.resource_manager)
        
        # Metrics and Diagnostics
        self.metrics_tracker = ClusterMetricsTracker()
        self.diagnostics_logger = ClusterDiagnostics()
        self.autoscaler = Autoscaler()

        # Dummy placeholder to avoid circular callbacks before wiring
        def _dummy(node_id, msg, req): pass
        self.fault_manager = FaultToleranceManager(_dummy)

        # Heartbeat Monitor
        self.heartbeat_monitor = HeartbeatMonitor(
            self.registry, 
            self.bus, 
            timeout_seconds=2.0,
            on_worker_failed_callback=self.fault_manager.handle_worker_failure
        )

        # Main Scheduler
        self.scheduler = DistributedScheduler(
            registry=self.registry,
            load_balancer=self.load_balancer,
            dispatcher=self.dispatcher,
            fault_manager=self.fault_manager,
            metrics=self.metrics_tracker,
            diagnostics=self.diagnostics_logger,
            autoscaler=self.autoscaler
        )

    async def start(self) -> None:
        """Starts background cluster loops and monitors."""
        await self.coordinator.start()
        await self.heartbeat_monitor.start()
        self.diagnostics_logger.log_event("CLUSTER_START", "Distributed Cluster coordinator initialized.")

    async def stop(self) -> None:
        """Stops background cluster loops and monitors."""
        await self.coordinator.stop()
        await self.heartbeat_monitor.stop()
        self.diagnostics_logger.log_event("CLUSTER_STOP", "Distributed Cluster coordinator stopped.")

    def register_worker(self, worker_id: str, resources: ResourceState, capabilities: List[Capability]) -> None:
        """Registers a worker directly into the coordinator registry."""
        self.registry.register_worker(worker_id, resources, capabilities)
        self.diagnostics_logger.log_event("REGISTER", f"Worker '{worker_id}' registered manually.")

    def unregister_worker(self, worker_id: str) -> None:
        """Unregisters a worker directly from the coordinator registry."""
        self.registry.unregister_worker(worker_id)
        self.diagnostics_logger.log_event("UNREGISTER", f"Worker '{worker_id}' unregistered manually.")

    async def submit(self, dag: OptimizedExecutionDAG, global_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Submits an Execution DAG for parallel execution across workers."""
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        self.diagnostics_logger.log_event("SUBMIT_JOB", f"Job '{job_id}' submitted with {len(dag.nodes)} nodes.")
        
        # Schedule the job on workers
        return await self.scheduler.schedule(job_id, dag, global_inputs)

    def cancel(self, job_id: str) -> None:
        """Triggers cancellation requests for running dispatches."""
        self.diagnostics_logger.log_warning(f"Job cancellation requested for job '{job_id}'.")
        # In a real environment, this would publish a cancellation payload to active workers.

    def status(self) -> Dict[str, Any]:
        """Returns details on online workers and diagnostics logs."""
        active = self.registry.list_active_workers()
        reports = self.diagnostics_logger.get_report()
        return {
            "online_workers": active,
            "status": "healthy" if len(active) > 0 else "degraded",
            "diagnostics": reports
        }

    def metrics(self) -> Dict[str, Any]:
        """Returns cluster resource utilizations and latencies."""
        active_count = len(self.registry.list_active_workers())
        # Aggregate total pending queue length based on active tasks running
        pending_count = sum(w["active_tasks"] for w in self.registry.workers.values())
        return self.metrics_tracker.get_summary(active_count, pending_count)
