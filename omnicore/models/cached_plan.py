import time
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from omnicore.ir.models import TaskIR
from omnicore.optimizer.optimization_context import OptimizedExecutionDAG

class CachedPlan(BaseModel):
    """
    Represents an optimized execution plan cached in the database.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    plan_id: str
    normalized_signature: str
    task_ir: TaskIR
    execution_dag: OptimizedExecutionDAG
    compiler_version: str = "1.0.0"
    optimizer_version: str = "1.0.0"
    timestamp: float = Field(default_factory=time.time)
