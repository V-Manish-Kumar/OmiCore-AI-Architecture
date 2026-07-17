from typing import Dict, Any, List
from pydantic import BaseModel, Field
from omnicore.execution.execution_node import RuntimeNodeStatus, ExecutionNodeState

class ExecutionResult(BaseModel):
    """
    Standardized result structure returned after adaptive execution.
    """
    plan_id: str
    status: RuntimeNodeStatus
    outputs: Dict[str, Any] = Field(default_factory=dict)
    node_results: Dict[str, ExecutionNodeState] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    diagnostics: List[str] = Field(default_factory=list)
