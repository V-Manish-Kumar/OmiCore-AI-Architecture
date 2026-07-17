import time
from typing import Optional
from omnicore.ir.models import TaskIR
from omnicore.models.execution_strategy import ExecutionStrategy, StrategyConfig
from omnicore.models.planner_result import PlannerResult
from omnicore.planner.planning_context import PlanningContext
from omnicore.planner.strategy_selector import StrategySelector
from omnicore.planner.cost_model import PlannerCostModel
from omnicore.planner.confidence_model import PlannerConfidenceModel
from omnicore.planner.execution_predictor import PlannerExecutionPredictor
from omnicore.planner.adaptive_rules import AdaptiveRulesEngine
from omnicore.planner.optimization_selector import PlannerOptimizationSelector
from omnicore.memory.procedural_memory import ProceduralMemory

class AdaptivePlanner:
    """
    Orchestrator for execution planning. Analyses task properties, computes
    costs, runs performance predictions, gathers diagnostics, and recommends
    strategies prior to execution.
    """
    def plan(self, task_ir: TaskIR, memory: Optional[ProceduralMemory] = None) -> PlannerResult:
        # 1. Initialize Planning Context
        context = PlanningContext(task_ir=task_ir)
        
        # 2. Select Execution Strategy
        strategy, config = StrategySelector.select_strategy(task_ir, memory)
        context.metrics.decisions_made.append(f"Selected strategy: {strategy.value}")

        # 3. Estimate cost, tokens and resources
        cost_res = PlannerCostModel.estimate_resources(task_ir)
        context.metrics.decisions_made.append("Estimated token usage and cost")

        # 4. Predict runtime metrics
        pred_res = PlannerExecutionPredictor.predict_execution(task_ir, config.enable_parallel_execution)
        context.metrics.decisions_made.append("Predicted execution latency and bottlenecks")

        # 5. Predict confidence probability
        confidence = PlannerConfidenceModel.predict_confidence(task_ir, memory)
        context.metrics.decisions_made.append("Evaluated historical reliability confidence")

        # 6. Gather diagnostics (rules + optimization recommendations)
        rule_diagnostics = AdaptiveRulesEngine.evaluate_rules(task_ir)
        opt_diagnostics = PlannerOptimizationSelector.recommend_optimizations(strategy, config)
        
        all_diagnostics = rule_diagnostics + opt_diagnostics
        context.diagnostics.extend(all_diagnostics)

        # 7. Record planning timing metrics
        duration_ms = (time.perf_counter() - context.start_time) * 1000.0
        context.metrics.planning_time_ms = round(duration_ms, 3)

        # Build results
        return PlannerResult(
            task_id=task_ir.task_id,
            execution_strategy=strategy,
            strategy_config=config,
            confidence_score=confidence,
            estimated_runtime=pred_res["estimated_runtime"],
            estimated_cost=cost_res["estimated_cost"],
            estimated_tokens=cost_res["estimated_tokens"],
            recommended_passes=list(config.recommended_passes),
            diagnostics=all_diagnostics
        )
