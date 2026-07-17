from typing import List, Dict, Any
from pydantic import BaseModel, Field
from omnicore.ir.enums import Capability

class OntologyTool(BaseModel):
    """
    Semantic definition of a service, agent, or tool capability provider.
    """
    name: str
    supported_capabilities: List[Capability] = Field(default_factory=list)
    provider: str
    properties: Dict[str, Any] = Field(default_factory=dict)
