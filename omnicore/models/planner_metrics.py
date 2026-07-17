from typing import List
from pydantic import BaseModel, Field

class PlannerMetrics(BaseModel):
    """
    Performance and operational metrics collected during planning cycles.
    """
    planning_time_ms: float = 0.0
    historical_lookup_hits: int = 0
    historical_lookup_misses: int = 0
    decisions_made: List[str] = Field(default_factory=list)
