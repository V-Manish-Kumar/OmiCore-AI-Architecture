from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class ExecutionStrategy(str, Enum):
    SEQUENTIAL = "Sequential"
    PARALLEL = "Parallel"
    COST_OPTIMIZED = "CostOptimized"
    LATENCY_OPTIMIZED = "LatencyOptimized"
    HIGH_RELIABILITY = "HighReliability"
    LOW_COST = "LowCost"
    BALANCED = "Balanced"

class StrategyConfig(BaseModel):
    """
    Execution configuration settings chosen by the planner.
    """
    execution_strategy: ExecutionStrategy = ExecutionStrategy.BALANCED
    retry_max_attempts: int = 3
    retry_base_delay: float = 0.1
    enable_parallel_execution: bool = True
    enable_graph_optimizations: bool = True
    caching_strategy: str = "lru"
    recommended_passes: List[str] = Field(default_factory=list)
