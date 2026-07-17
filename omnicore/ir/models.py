from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from omnicore.ir.enums import TaskIntent, Capability, Complexity, NodeStatus

class Dependency(BaseModel):
    source: str
    target: str

    def to_tuple(self) -> tuple[str, str]:
        return (self.source, self.target)

class ExecutionNode(BaseModel):
    node_id: str
    name: str
    description: str
    capability: Capability
    input: Any = None
    output: Any = None
    status: NodeStatus = NodeStatus.PENDING
    estimated_cost: Optional[float] = 0.0
    estimated_time: Optional[float] = 0.0  # estimated time in seconds
    parallelizable: bool = True

class ExecutionDAG(BaseModel):
    nodes: List[ExecutionNode] = Field(default_factory=list)
    dependencies: List[Dependency] = Field(default_factory=list)
    topological_order: List[str] = Field(default_factory=list)

class TaskIR(BaseModel):
    task_id: str
    primary_intent: TaskIntent = TaskIntent.UNKNOWN
    secondary_intent: Optional[TaskIntent] = None
    domain: str = "general"
    user_goal: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    required_capabilities: List[Capability] = Field(default_factory=list)
    estimated_complexity: Complexity = Complexity.MEDIUM
    confidence_score: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
