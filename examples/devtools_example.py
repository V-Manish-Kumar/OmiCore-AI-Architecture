import sys
import os
import asyncio
import json
import time

# Ensure the root package directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omnicore.parser.intent_parser import IntentParser
from omnicore.optimizer.optimizer import TaskOptimizer
from omnicore.devtools.debugger import CompilerDebugger
from omnicore.devtools.profiler import PerformanceProfiler
from omnicore.devtools.tracer import Tracer
from omnicore.visualization.dag_visualizer import DAGVisualizer
from omnicore.dashboard.server import DashboardServer
from omnicore.dashboard.api import wire_devtools
from omnicore.distributed.cluster_manager import DistributedClusterManager
from omnicore.cluster.resource import ResourceState
from omnicore.ir.enums import Capability

async def main():
    print("=" * 80)
    print("OMNICORE DEVELOPER PLATFORM & COMPILER OBSERVABILITY SHOWCASE")
    print("=" * 80)

    # 1. Setup Tracer, Profiler, and Cluster Coordinator
    tracer = Tracer()
    profiler = PerformanceProfiler()
    cluster = DistributedClusterManager()
    
    # Wire instances to the dashboard API
    wire_devtools(cluster, tracer, profiler)
    print("\n[1] Observability Tracer and Performance Profiler initialized.")

    # 2. Run Debugger with step-through breakpoints
    print("\n[2] Setting breakpoins and stepping through compilation...")
    debugger = CompilerDebugger()
    debugger.set_breakpoint("parsing")
    debugger.set_breakpoint("optimization")

    def breakpoint_callback(phase: str, state):
        print(f"  >>> [Debugger breakpoint hit!] Phase: '{phase}'")
        print(f"      State details: {state}")

    debugger.breakpoint_handler = breakpoint_callback

    query = "Search Google for python libraries and summarize findings."
    
    # Simulate compiler compiler steps
    tracer.start_span("parsing", "frontend")
    t0 = time.perf_counter()
    parser = IntentParser()
    task_ir, raw_dag = parser.compile(query)
    duration_parse = time.perf_counter() - t0
    profiler.record_phase("parsing", duration_parse)
    tracer.end_span("parsing")
    debugger.step("parsing", {"task_id": task_ir.task_id, "nodes_count": len(raw_dag.nodes)})

    tracer.start_span("optimization", "optimizer")
    t1 = time.perf_counter()
    optimizer = TaskOptimizer()
    opt_dag, report = optimizer.optimize(task_ir, raw_dag)
    duration_opt = time.perf_counter() - t1
    profiler.record_phase("optimization", duration_opt)
    tracer.end_span("optimization")
    debugger.step("optimization", {"applied_passes": report.optimization_passes_applied})

    # 3. Generate Mermaid visualization
    print("\n[3] Rendering Optimized Execution DAG as Mermaid Flowchart:")
    mermaid_code = DAGVisualizer.visualize(opt_dag)
    print("-" * 40)
    print(mermaid_code)
    print("-" * 40)

    # 4. Start Observability Dashboard Dev Server
    print("\n[4] Starting FastAPI Observability Web Dashboard Server...")
    server = DashboardServer(host="127.0.0.1", port=8001)
    server.start()
    print("  >>> Web Console Dashboard available at: http://127.0.0.1:8001/")

    # Register worker so dashboard has nodes data
    res = ResourceState(total_cpu_cores=4.0, total_memory_mb=4096.0)
    cluster.register_worker("worker_observability_node", res, [Capability.WEB_SEARCH, Capability.SUMMARIZATION])

    # Simulate runtime events on the cluster
    print("  >>> Simulating task completions...")
    cluster.metrics_tracker.record_completion(0.08)
    cluster.metrics_tracker.record_completion(0.04)
    
    # Let server run for 2 seconds to showcase
    await asyncio.sleep(2.0)

    # 5. Export performance and tracing logs
    print("\n[5] Exporting Observability Telemetry Logs:")
    print("Performance Profiler Summary:")
    print(json.dumps(profiler.get_performance_report(), indent=2))
    
    # Shutting down server
    print("\n[6] Stopping Web Dashboard Server...")
    server.stop()
    print("  >>> Observability showcase completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
