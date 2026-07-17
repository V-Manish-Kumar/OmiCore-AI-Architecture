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
from omnicore.memory.procedural_memory import ProceduralMemory
from omnicore.memory.memory_manager import MemoryManager
from omnicore.storage.sqlite_store import SQLiteStore

async def main():
    print("=" * 80)
    print("OMNICORE PROCEDURAL MEMORY & PLAN REUSE SHOWCASE")
    print("=" * 80)

    # Initialize Compiler, Optimizer, Runtime, and Storage/Memory
    parser = IntentParser()
    optimizer = TaskOptimizer()
    adapter = MockCapabilityAdapter(latency=0.01) # fast runtime
    
    # Procedural memory backed by in-memory SQLite
    store = SQLiteStore(":memory:")
    memory = ProceduralMemory(store)
    manager = MemoryManager(memory)

    # Query 1: First time compiled and optimized (Cache Miss)
    query_1 = "Search Google for python ML libraries, compare findings and write a report."
    print(f"\n[Run 1] Input Instruction:\n  \"{query_1}\"")
    
    # 1. Compile or Retrieve
    opt_dag, cached_plan, task_ir = manager.compile_or_reuse(query_1, parser, optimizer)
    
    if cached_plan:
        print(f"  >>> Plan reuse triggered! Saved compile time.")
    else:
        print(f"  >>> Cache Miss! Compiled and optimized from scratch.")
        print(f"  >>> Optimized Nodes: {', '.join(n.node_id for n in opt_dag.nodes)}")

    # 2. Execute plan via Runtime
    runtime = AdaptiveRuntime(adapter=adapter)
    result = await runtime.execute(opt_dag, inputs={"query": "python ml"})
    print(f"  >>> Runtime finished status: {result.status.value}")

    # 3. Store in procedural memory
    manager.record_execution(task_ir, opt_dag, result.plan_id, result)
    print("  >>> Execution record saved in Procedural Memory.")

    # -------------------------------------------------------------
    # Query 2: Similar intent/capabilities with different wording (Cache Hit!)
    query_2 = "Find python machine learning libraries on Google, analyze comparison and generate document."
    print("\n" + "-" * 80)
    print(f"[Run 2] Similar Instruction (Different Wording):\n  \"{query_2}\"")
    
    # 1. Compile or Retrieve (should retrieve Query 1 plan!)
    opt_dag_2, cached_plan_2, task_ir_2 = manager.compile_or_reuse(query_2, parser, optimizer, similarity_threshold=0.80)
    
    if cached_plan_2:
        print(f"  >>> [Cache Hit!] Reused optimized plan '{cached_plan_2.plan_id}' from memory.")
        print(f"  >>> Reused DAG Nodes: {', '.join(n.node_id for n in opt_dag_2.nodes)}")
    else:
        print(f"  >>> Cache Miss! Compiled and optimized from scratch.")

    # 2. Execute plan via Runtime
    result_2 = await runtime.execute(opt_dag_2, inputs={"query": "python ml"})
    print(f"  >>> Runtime finished status: {result_2.status.value}")

    # 3. Store in procedural memory
    manager.record_execution(task_ir_2, opt_dag_2, cached_plan_2.plan_id if cached_plan_2 else result_2.plan_id, result_2)
    print("  >>> Execution record saved in Procedural Memory.")

    # -------------------------------------------------------------
    # Print Memory Statistics
    stats = memory.statistics()
    print("\n" + "=" * 80)
    print("PROCEDURAL MEMORY METRIC STATISTICS")
    print("=" * 80)
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
