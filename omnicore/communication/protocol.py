from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from omnicore.ir.enums import Capability
from omnicore.cluster.resource import ResourceState

class HeartbeatMessage(BaseModel):
    worker_id: str
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    timestamp: float = Field(default_factory=lambda: 0.0) # populated at runtime

class TaskSubmitMessage(BaseModel):
    job_id: str
    node_id: str
    capability: Capability
    inputs: Dict[str, Any] = Field(default_factory=dict)
    resource_req: Dict[str, Any] = Field(default_factory=dict) # serialize ResourceRequirement

class TaskResultMessage(BaseModel):
    job_id: str
    node_id: str
    success: bool
    outputs: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    worker_id: str

class WorkerRegisterMessage(BaseModel):
    worker_id: str
    resources: ResourceState
    capabilities: List[Capability]
