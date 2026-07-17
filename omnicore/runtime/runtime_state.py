from typing import Dict, Any
from pydantic import BaseModel, Field
from omnicore.execution.execution_node import RuntimeNodeStatus, ExecutionNodeState

class RuntimeState(BaseModel):
    """
    Maintains the dynamic runtime progress, including completed task variables,
    node statuses, and failure statistics.
    Can be serialized for checkpointing.
    """
    plan_id: str
    node_statuses: Dict[str, RuntimeNodeStatus] = Field(default_factory=dict)
    node_states: Dict[str, ExecutionNodeState] = Field(default_factory=dict)
    variables: Dict[str, Any] = Field(default_factory=dict)
