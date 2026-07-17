from typing import List
from pydantic import BaseModel, Field
from omnicore.execution.execution_node import RuntimeNodeStatus

class ExecutionStage(BaseModel):
    """
    Represents a group of execution nodes scheduled to run in parallel in the execution plan.
    """
    stage_index: int
    node_ids: List[str] = Field(default_factory=list)
    status: RuntimeNodeStatus = RuntimeNodeStatus.PENDING
