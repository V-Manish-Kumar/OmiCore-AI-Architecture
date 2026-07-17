from typing import List
from omnicore.models.execution_strategy import ExecutionStrategy, StrategyConfig
from omnicore.planner.diagnostics import PlannerDiagnostic, PlannerDiagnosticSeverity

class PlannerOptimizationSelector:
    """
    Recommends which compiler passes to execute based on the selected execution strategy.
    """
    @staticmethod
    def recommend_optimizations(strategy: ExecutionStrategy, config: StrategyConfig) -> List[PlannerDiagnostic]:
        diagnostics = []

        if strategy in (ExecutionStrategy.COST_OPTIMIZED, ExecutionStrategy.LOW_COST):
            diagnostics.append(PlannerDiagnostic(
                severity=PlannerDiagnosticSeverity.SUGGESTION,
                message="Cost optimization strategy enabled.",
                suggestion="Recommended: Enable aggressive Dead Node Elimination and Common Subexpression Elimination (CSE)."
            ))
            
        if strategy == ExecutionStrategy.SEQUENTIAL:
            diagnostics.append(PlannerDiagnostic(
                severity=PlannerDiagnosticSeverity.SUGGESTION,
                message="Sequential execution strategy chosen.",
                suggestion="Omit parallelization passes to reduce schedule overhead."
            ))

        if strategy == ExecutionStrategy.LATENCY_OPTIMIZED:
            diagnostics.append(PlannerDiagnostic(
                severity=PlannerDiagnosticSeverity.SUGGESTION,
                message="Latency optimization strategy enabled.",
                suggestion="Enable in-memory LRU caching to skip compilation overhead."
            ))

        return diagnostics
