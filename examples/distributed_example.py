import sys
import os
import asyncio
import json

# Ensure the root package directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omnicore.ir.enums import Capability
from omnicore.optimizer.optimization_context import OptimizedExecutionNode, OptimizedExecutionDAG
from omnicore.cluster.resource import ResourceState
from omnicore.cluster.worker import ClusterWorker
from omnicore.communication.message_bus import LocalMessageBus
from omnicore.distributed.cluster_manager import DistributedClusterManager

def create_demo_dag() -> OptimizedExecutionDAG:
    # Build 3-node pipeline: web_search -> summarization -> pdf_generation
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
    n3 = OptimizedExecutionNode(
        node_id="pdf_1",
        name="PDF Compiler",
        description="Generate report PDF",
        capability=Capability.PDF_GENERATION,
        input="summary",
        output="pdf_filepath"
    )
    return OptimizedExecutionDAG(
        nodes=[n1, n2, n3],
        topological_order=["search_1", "summarize_1", "pdf_1"]
    )

async def main():
    print("=" * 80)
    print("OMNICORE DISTRIBUTED RUNTIME & RESOURCE ORCHESTRATOR DEMO")
    print("=" * 80)

    # 1. Initialize message broker and cluster coordinator
    bus = LocalMessageBus()
    cluster = DistributedClusterManager(bus)
    await cluster.start()

    # 2. Spin up and register 3 worker nodes with distinct capabilities
    res = ResourceState(total_cpu_cores=4.0, total_memory_mb=4096.0)
    
    worker1 = ClusterWorker("worker_search_node", [Capability.WEB_SEARCH], res, bus, heartbeat_interval=0.1)
    worker2 = ClusterWorker("worker_summary_node", [Capability.SUMMARIZATION], res, bus, heartbeat_interval=0.1)
    worker3 = ClusterWorker("worker_pdf_node", [Capability.PDF_GENERATION], res, bus, heartbeat_interval=0.1)

    print("\n[1] Starting Cluster Workers...")
    await worker1.start()
    await worker2.start()
    await worker3.start()
    
    # Wait for coordinator to receive register messages
    await asyncio.sleep(0.2)
    print(f"  >>> Active Workers registered: {cluster.registry.list_active_workers()}")

    # 3. Submit 3-node Execution DAG
    dag = create_demo_dag()
    print(f"\n[2] Submitting Execution DAG Workflow ({len(dag.nodes)} nodes: search -> summarize -> pdf):")
    
    start_time = asyncio.get_running_loop().time()
    results = await cluster.submit(dag, {"query": "distributed task compiler"})
    duration = asyncio.get_running_loop().time() - start_time
    
    print("\n[3] Execution Results:")
    print(json.dumps(results, indent=2))
    print(f"  >>> Total workflow latency: {duration:.3f} seconds.")

    # 4. Print Cluster Statistics and Timeline Logs
    print("\n" + "=" * 80)
    print("CLUSTER METRICS SUMMARY")
    print("=" * 80)
    print(json.dumps(cluster.metrics(), indent=2))

    print("\n" + "=" * 80)
    print("COORDINATOR DIAGNOSTIC TIMELINE")
    print("=" * 80)
    status_report = cluster.status()
    for item in status_report["diagnostics"]["timeline"]:
        print(f"  [{item['event_type']}] {item['message']}")

    # 5. Shutdown workers and cluster coordinator
    print("\n[4] Stopping Cluster Workers and Coordinator...")
    await worker1.stop()
    await worker2.stop()
    await worker3.stop()
    await cluster.stop()
    print("  >>> Demo finished successfully.")

if __name__ == "__main__":
    asyncio.run(main())
