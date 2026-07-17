from typing import Optional, Tuple
from omnicore.ir.models import TaskIR
from omnicore.models.execution_strategy import ExecutionStrategy, StrategyConfig
from omnicore.planner.strategy_repository import STRATEGY_BLUEPRINTS
from omnicore.memory.procedural_memory import ProceduralMemory

class StrategySelector:
    """
    Selects the optimal execution strategy based on task goals,
    constraints, capability count, and historical performance metrics.
    """
    @staticmethod
    def select_strategy(task_ir: TaskIR, memory: Optional[ProceduralMemory] = None) -> Tuple[ExecutionStrategy, StrategyConfig]:
        strategy = ExecutionStrategy.BALANCED
        
        # 1. Analyze constraints
        constraints_str = " ".join(task_ir.constraints).lower()
        
        if any(word in constraints_str for word in ["fast", "speed", "latency", "realtime", "quick"]):
            strategy = ExecutionStrategy.LATENCY_OPTIMIZED
        elif any(word in constraints_str for word in ["cheap", "budget", "lowcost", "frugal"]):
            strategy = ExecutionStrategy.LOW_COST
        elif any(word in constraints_str for word in ["reliable", "critical", "transactional", "safety", "secure"]):
            strategy = ExecutionStrategy.HIGH_RELIABILITY

        # Check critical capabilities directly
        from omnicore.ir.enums import Capability
        critical_caps = {Capability.EMAIL, Capability.DATABASE_ACCESS}
        if critical_caps.intersection(set(task_ir.required_capabilities)):
            strategy = ExecutionStrategy.HIGH_RELIABILITY

        # 2. Check capability metrics
        # Sequential execution is preferred for single-node graphs to avoid scheduling overheads
        if len(task_ir.required_capabilities) <= 1 and strategy == ExecutionStrategy.BALANCED:
            strategy = ExecutionStrategy.SEQUENTIAL

        # 3. Check history for failure rates
        if memory:
            try:
                records = memory.repository.list_records()
                if records:
                    # Find similar runs sharing capabilities
                    relevant = [
                        r for r in records 
                        if set(task_ir.required_capabilities).intersection(set(r.task_ir.required_capabilities))
                    ]
                    if relevant:
                        avg_success = sum(r.success_rate for r in relevant) / len(relevant)
                        # Switch to HighReliability if history shows low success rates (< 80%)
                        if avg_success < 0.80:
                            strategy = ExecutionStrategy.HIGH_RELIABILITY
            except Exception:
                pass

        config = STRATEGY_BLUEPRINTS[strategy]
        return strategy, config
