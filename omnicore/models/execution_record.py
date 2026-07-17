import time
import uuid
from pydantic import BaseModel, Field, ConfigDict
from omnicore.ir.models import TaskIR
from omnicore.optimizer.optimization_context import OptimizedExecutionDAG

class ExecutionRecord(BaseModel):
    """
    Represents historical execution log results saved in procedural memory.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    record_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:8]}")
    task_id: str
    plan_id: str
    normalized_signature: str
    task_ir: TaskIR
    execution_dag: OptimizedExecutionDAG
    execution_time: float
    cost: float
    tokens: int
    confidence: float
    success_rate: float
    timestamp: float = Field(default_factory=time.time)
    compiler_version: str = "1.0.0"
    runtime_version: str = "1.0.0"
