from typing import Tuple, Optional, Dict, Any
from omnicore.parser.intent_parser import IntentParser
from omnicore.optimizer.optimizer import TaskOptimizer
from omnicore.optimizer.optimization_context import OptimizedExecutionDAG
from omnicore.ir.models import TaskIR
from omnicore.models.cached_plan import CachedPlan
from omnicore.models.execution_record import ExecutionRecord
from omnicore.memory.procedural_memory import ProceduralMemory
from omnicore.storage.sqlite_store import SQLiteStore
from omnicore.memory.similarity import generate_signature

class MemoryManager:
    """
    Integrates the Front-end Compiler, Graph Optimizer, and Procedural Memory.
    Allows reusing previously compiled/optimized execution DAGs to skip the compilation stage.
    """
    def __init__(self, memory: Optional[ProceduralMemory] = None):
        # Default to an in-memory SQLite store if no memory instance is supplied
        self.memory = memory or ProceduralMemory(SQLiteStore())

    def compile_or_reuse(
        self, 
        query: str, 
        parser: IntentParser, 
        optimizer: TaskOptimizer,
        similarity_threshold: float = 0.85
    ) -> Tuple[OptimizedExecutionDAG, Optional[CachedPlan], TaskIR]:
        """
        Runs front-end compilation to retrieve the TaskIR, then searches procedural memory
        for an existing optimized execution plan. If found, returns the cached DAG.
        Otherwise, compiles/optimizes from scratch.
        """
        # Step 1: Lex, Parse AST, and Lower to TaskIR (using front-end compiler)
        # Note: compile returns (task_ir, execution_dag)
        task_ir, raw_dag = parser.compile(query)
        
        # Step 2: Query memory
        cached_plan = self.memory.retrieve(task_ir, similarity_threshold)
        
        if cached_plan:
            # Plan reuse (Cache hit)
            return cached_plan.execution_dag, cached_plan, task_ir
            
        # Cache miss: Run optimization pipeline
        opt_dag, report = optimizer.optimize(task_ir, raw_dag)
        
        return opt_dag, None, task_ir

    def record_execution(
        self,
        task_ir: TaskIR,
        opt_dag: OptimizedExecutionDAG,
        plan_id: str,
        runtime_result: Any
    ) -> None:
        """
        Creates and stores an ExecutionRecord log entry after running a plan in the runtime.
        """
        sig = generate_signature(task_ir)
        
        record = ExecutionRecord(
            task_id=task_ir.task_id,
            plan_id=plan_id,
            normalized_signature=sig,
            task_ir=task_ir,
            execution_dag=opt_dag,
            execution_time=runtime_result.metrics.get("total_runtime_seconds", 0.0),
            cost=runtime_result.metrics.get("total_cost", 0.0) or runtime_result.outputs.get("cost", 0.0),
            tokens=runtime_result.metrics.get("total_tokens", 0) or runtime_result.outputs.get("tokens", 0),
            confidence=task_ir.confidence_score,
            success_rate=runtime_result.metrics.get("success_rate", 1.0)
        )
        
        self.memory.store(record)
