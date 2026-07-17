import sys
import os
import asyncio
import json

# Ensure the root package directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omnicore.parser.intent_parser import IntentParser
from omnicore.optimizer.optimizer import TaskOptimizer
from omnicore.runtime.runtime import AdaptiveRuntime
from omnicore.runtime.adapters.capability_adapter import MockCapabilityAdapter
from omnicore.runtime.event_bus import Event

async def run_end_to_end(query: str):
    print("\n" + "=" * 80)
    print(f"OMNICORE END-TO-END EXECUTION RUN")
    print(f"Prompt: \"{query}\"")
    print("=" * 80)

    try:
        # Step 1: Front-end Compilation (Module 1)
        print("\n[Step 1] Compiling Prompt into Task IR and Initial DAG...")
        parser = IntentParser()
        task_ir, execution_dag = parser.compile(query)
        print(f"  - Generated Task ID: {task_ir.task_id}")
        print(f"  - Initial Nodes count: {len(execution_dag.nodes)}")

        # Step 2: Optimization Pipeline (Module 2)
        print("\n[Step 2] Optimizing execution graph...")
        optimizer = TaskOptimizer()
        opt_dag, opt_report = optimizer.optimize(task_ir, execution_dag)
        print(f"  - Optimized Nodes count: {len(opt_dag.nodes)}")
        print(f"  - Removed/Merged: {len(opt_report.removed_nodes)} node(s)")
        print(f"  - Scheduled stages: {len(opt_dag.stages)} stages")

        # Step 3: Execution Runtime (Module 3)
        print("\n[Step 3] Launching Adaptive Runtime execution...")
        adapter = MockCapabilityAdapter(latency=0.08) # 80ms latency per node
        runtime = AdaptiveRuntime(adapter=adapter)

        # Let's log node lifecycle events via the Event Bus
        def on_event(event: Event):
            print(f"  >>> Event [Bus]: {event.event_type} - {json.dumps(event.data)}")

        runtime.context.event_bus.subscribe("*", on_event)

        # Run execution
        print("\nExecuting graph tasks concurrently...")
        result = await runtime.execute(opt_dag, inputs={"query": "machine learning servers"})

        print("\n" + "-" * 80)
        print("EXECUTION RESULTS SUMMARY")
        print("-" * 80)
        print(f"Plan Execution ID: {result.plan_id}")
        print(f"Execution Status:  {result.status.value}")
        print(f"Peak Parallelism:  {result.metrics['peak_parallelism']}")
        print(f"Total Runtime:     {result.metrics['total_runtime_seconds']:.4f} seconds")
        print(f"Total Retries:     {result.metrics['total_retries']}")
        print(f"Final Outputs:     {json.dumps(result.outputs, indent=2)}")
        print("\nNode details:")
        for nid, ns in result.node_results.items():
            time_str = f"{ns.execution_time:.3f}s" if ns.execution_time else "N/A"
            print(f"  - [{nid}] status={ns.status.value} time={time_str} outputs={list(ns.output_data.keys())}")

    except Exception as e:
        print(f"\n[!] Run failed: {e}")

async def main():
    # Execute a query that has independent branches that will run in parallel
    query = (
        "Search GitHub for web servers, search Arxiv for web servers, "
        "compare the servers, and generate a PDF report."
    )
    await run_end_to_end(query)

if __name__ == "__main__":
    asyncio.run(main())
