import sys
import os
import json

# Ensure the root package directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omnicore.parser.intent_parser import IntentParser
from omnicore.planner.planner import AdaptivePlanner

def run_planning_showcase(query: str):
    print("\n" + "=" * 80)
    print(f"ADAPTIVE PLANNER RUN")
    print(f"Prompt: \"{query}\"")
    print("=" * 80)

    try:
        # Step 1: Frontend compilation to get TaskIR
        parser = IntentParser()
        task_ir, _ = parser.compile(query)

        # Step 2: Run Adaptive Planner
        planner = AdaptivePlanner()
        plan_result = planner.plan(task_ir)

        print(f"\nExecution Decisions:")
        print(f"  - Selected Strategy:       {plan_result.execution_strategy.value}")
        print(f"  - Max Retry Attempts:     {plan_result.strategy_config.retry_max_attempts}")
        print(f"  - Parallel Execution:      {plan_result.strategy_config.enable_parallel_execution}")
        print(f"  - Graph Optimizations:     {plan_result.strategy_config.enable_graph_optimizations}")
        print(f"  - Recommended Passes:      {', '.join(plan_result.recommended_passes)}")
        
        print(f"\nResource & Cost Predictions:")
        print(f"  - Predicted Confidence:    {plan_result.confidence_score * 100:.1f}%")
        print(f"  - Projected Parallel Time: {plan_result.estimated_runtime} seconds")
        print(f"  - Estimated API Cost:      ${plan_result.estimated_cost:.4f}")
        print(f"  - Expected Token usage:    {plan_result.estimated_tokens} tokens")

        if plan_result.diagnostics:
            print(f"\nPlanner Diagnostics & Risk Assessments:")
            for d in plan_result.diagnostics:
                print(f"  [{d.severity.value}] {d.message}")
                if d.suggestion:
                    print(f"    Suggestion: {d.suggestion}")

    except Exception as e:
        print(f"[!] Planning failed: {e}")

def main():
    queries = [
        # Example 1: Default sequential planning (1 capability)
        "Summarize this document.",
        # Example 2: Latency-optimized parallel planning (multi-node)
        "Search Google for python ML libraries, compare findings and write a report. Speed constraint: make it quick.",
        # Example 3: Low-cost planning (budget constraints)
        "Search GitHub for web servers, compare results. Cost constraint: lowcost budget.",
        # Example 4: High reliability (side-effects and automated actions)
        "Search databases for transactions and email the admin report."
    ]

    for q in queries:
        run_planning_showcase(q)
        print("\n" + "#" * 80 + "\n")

if __name__ == "__main__":
    main()
