import time
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from omnicore.ir.models import TaskIR
from omnicore.models.planner_metrics import PlannerMetrics
from omnicore.planner.diagnostics import PlannerDiagnostic

class PlanningContext(BaseModel):
    """
    Session context tracking state, diagnostics, and metrics during a single planning run.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    task_ir: TaskIR
    start_time: float = Field(default_factory=time.perf_counter)
    metrics: PlannerMetrics = Field(default_factory=PlannerMetrics)
    diagnostics: List[PlannerDiagnostic] = Field(default_factory=list)
