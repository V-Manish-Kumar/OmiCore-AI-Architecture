from typing import Dict
from omnicore.models.execution_strategy import ExecutionStrategy, StrategyConfig

# Default strategy blueprints
STRATEGY_BLUEPRINTS: Dict[ExecutionStrategy, StrategyConfig] = {
    ExecutionStrategy.SEQUENTIAL: StrategyConfig(
        execution_strategy=ExecutionStrategy.SEQUENTIAL,
        retry_max_attempts=3,
        retry_base_delay=0.1,
        enable_parallel_execution=False,
        enable_graph_optimizations=True,
        recommended_passes=[
            "validation", "capability_resolution", "dependency_analysis", 
            "graph_optimization", "cost_estimation", "scheduling", "optimization_report"
        ]
    ),
    ExecutionStrategy.PARALLEL: StrategyConfig(
        execution_strategy=ExecutionStrategy.PARALLEL,
        retry_max_attempts=3,
        retry_base_delay=0.1,
        enable_parallel_execution=True,
        enable_graph_optimizations=True,
        recommended_passes=[
            "validation", "capability_resolution", "dependency_analysis", 
            "parallelization", "graph_optimization", "cost_estimation", "scheduling", "optimization_report"
        ]
    ),
    ExecutionStrategy.COST_OPTIMIZED: StrategyConfig(
        execution_strategy=ExecutionStrategy.COST_OPTIMIZED,
        retry_max_attempts=2,
        retry_base_delay=0.1,
        enable_parallel_execution=True,
        enable_graph_optimizations=True,
        caching_strategy="aggressive_lru",
        # Custom passes order prioritizing graph deduplication/pruning
        recommended_passes=[
            "validation", "capability_resolution", "dependency_analysis", 
            "graph_optimization", "cost_estimation", "scheduling", "optimization_report"
        ]
    ),
    ExecutionStrategy.LATENCY_OPTIMIZED: StrategyConfig(
        execution_strategy=ExecutionStrategy.LATENCY_OPTIMIZED,
        retry_max_attempts=2,
        retry_base_delay=0.05,
        enable_parallel_execution=True,
        enable_graph_optimizations=True,
        recommended_passes=[
            "validation", "capability_resolution", "dependency_analysis", 
            "parallelization", "graph_optimization", "cost_estimation", "scheduling", "optimization_report"
        ]
    ),
    ExecutionStrategy.HIGH_RELIABILITY: StrategyConfig(
        execution_strategy=ExecutionStrategy.HIGH_RELIABILITY,
        retry_max_attempts=5,
        retry_base_delay=0.5,
        enable_parallel_execution=True,
        enable_graph_optimizations=True,
        recommended_passes=[
            "validation", "capability_resolution", "dependency_analysis", 
            "parallelization", "graph_optimization", "cost_estimation", "scheduling", "optimization_report"
        ]
    ),
    ExecutionStrategy.LOW_COST: StrategyConfig(
        execution_strategy=ExecutionStrategy.LOW_COST,
        retry_max_attempts=2,
        retry_base_delay=0.1,
        enable_parallel_execution=True,
        enable_graph_optimizations=True,
        caching_strategy="aggressive_lru",
        recommended_passes=[
            "validation", "capability_resolution", "dependency_analysis", 
            "graph_optimization", "scheduling"  # Skip report overhead
        ]
    ),
    ExecutionStrategy.BALANCED: StrategyConfig(
        execution_strategy=ExecutionStrategy.BALANCED,
        retry_max_attempts=3,
        retry_base_delay=0.1,
        enable_parallel_execution=True,
        enable_graph_optimizations=True,
        recommended_passes=[
            "validation", "capability_resolution", "dependency_analysis", 
            "parallelization", "graph_optimization", "cost_estimation", "scheduling", "optimization_report"
        ]
    )
}
