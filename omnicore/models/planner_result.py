from typing import List, Any
from pydantic import BaseModel, Field
from omnicore.models.execution_strategy import ExecutionStrategy, StrategyConfig

class PlannerResult(BaseModel):
    """
    Structured planning recommendations output by the Adaptive Planner.
    """
    task_id: str
    execution_strategy: ExecutionStrategy
    strategy_config: StrategyConfig
    confidence_score: float
    estimated_runtime: float
    estimated_cost: float
    estimated_tokens: int
    recommended_passes: List[str] = Field(default_factory=list)
    diagnostics: List[Any] = Field(default_factory=list)
