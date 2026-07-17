from enum import Enum
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field, ConfigDict
from omnicore.optimizer.optimization_context import OptimizedExecutionNode

class RuntimeNodeStatus(str, Enum):
    PENDING = "Pending"
    READY = "Ready"
    RUNNING = "Running"
    COMPLETED = "Completed"
    FAILED = "Failed"
    CANCELLED = "Cancelled"

class ExecutionNodeState(BaseModel):
    """
    Tracks runtime execution state and statistics for a single node.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    node: OptimizedExecutionNode
    status: RuntimeNodeStatus = RuntimeNodeStatus.PENDING
    retry_count: int = 0
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    error_message: Optional[str] = None
    output_data: Dict[str, Any] = Field(default_factory=dict)
    execution_time: Optional[float] = None
