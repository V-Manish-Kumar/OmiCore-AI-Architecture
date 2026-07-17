import sys
import os
import json

# Ensure the root package directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omnicore.parser.intent_parser import IntentParser, CompileError
from omnicore.optimizer.optimizer import TaskOptimizer
from omnicore.ir.serializer import serialize_to_dict

def run_optimization(query: str):
    print("\n" + "=" * 80)
    print(f"Compiling & Optimizing Prompt:\n  \"{query}\"")
    print("=" * 80)

    try:
        # Step 1: Front-end compiler (Lowering to Task IR & initial DAG)
        parser = IntentParser()
        task_ir, execution_dag = parser.compile(query)
        
        print("\n[Stage 1] Front-end Compilation Completed.")
        print(f"  - Initial Nodes: {len(execution_dag.nodes)} ({', '.join(n.node_id for n in execution_dag.nodes)})")

        # Step 2: Optimization Pipeline
        optimizer = TaskOptimizer()
        opt_dag, report = optimizer.optimize(task_ir, execution_dag)

        print("\n[Stage 2] Optimization Pipeline Completed.")
        
        print("\n" + "-" * 80)
        print("OPTIMIZATION REPORT SUMMARY")
        print("-" * 80)
        print(f"Original Nodes:     {len(report.original_nodes)} ({', '.join(report.original_nodes)})")
        print(f"Optimized Nodes:    {len(report.optimized_nodes)} ({', '.join(report.optimized_nodes)})")
        print(f"Removed Nodes:      {len(report.removed_nodes)} ({', '.join(report.removed_nodes)})")
        print(f"Merged Nodes Map:   {json.dumps(report.merged_nodes, indent=2)}")
        print(f"Parallel Groups:    {report.parallel_groups}")
        print(f"Critical Path:      {' -> '.join(report.critical_path)}")
        print(f"Estimated Runtime:  {report.estimated_runtime} seconds")
        print(f"Estimated API Cost: ${report.estimated_cost:.4f}")
        print(f"Estimated Tokens:   {report.estimated_tokens} tokens")
        print(f"Passes Applied:     {', '.join(report.optimization_passes_applied)}")
        
        if report.warnings:
            print("\nWarnings:")
            for w in report.warnings:
                print(f"  [!] {w}")

        print("\n" + "-" * 80)
        print("OPTIMIZED SCHEDULED STAGES")
        print("-" * 80)
        for idx, stage in enumerate(opt_dag.stages):
            print(f"Stage {idx}:")
            for node_id in stage:
                node = next(n for n in opt_dag.nodes if n.node_id == node_id)
                par_str = f"(Parallel Group: {node.parallel_group_id})" if node.parallel_group_id else "(Sequential)"
                print(f"  - [{node_id}] {node.name}")
                print(f"    Capability:  {node.capability.value} -> {node.resolved_capability.__class__.__name__}")
                print(f"    Scheduling:  {par_str}")
                print(f"    Inputs:      {node.input}")
                print(f"    Outputs:     {node.output}")
                print(f"    Estimated:   {node.estimated_time}s | {node.estimated_tokens} tokens | ${node.estimated_cost:.4f}")

    except CompileError as ce:
        print("\n[!] Compilation failed with errors:")
        for err in ce.errors:
            print(f"  - {err}")
    except Exception as e:
        print(f"\n[!] Optimizer Exception: {e}")

def main():
    # Example natural language instructions containing duplicates and sequence flows
    queries = [
        # Example 1: Parallel branches & sequence flow
        "Search Google for python machine learning libraries, search Google for python machine learning libraries, compare results, summarize findings and send email.",
        # Example 2: Duplicate capability search (will trigger deduplication)
        "Search Github for web servers, search Github for web servers, compare servers, and write a summary report."
    ]

    for q in queries:
        run_optimization(q)
        print("\n" + "#" * 80 + "\n")

if __name__ == "__main__":
    main()
