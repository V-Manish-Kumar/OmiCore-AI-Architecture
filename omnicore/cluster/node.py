from pydantic import BaseModel, Field
from typing import Dict, Any

class NodeInfo(BaseModel):
    """
    Metadata describing a network node in the cluster.
    """
    node_id: str
    host: str = "localhost"
    port: int = 8000
    properties: Dict[str, Any] = Field(default_factory=dict)
