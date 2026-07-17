from typing import Dict, Any
from pydantic import BaseModel, Field

class OntologyEntity(BaseModel):
    """
    Semantic definition of a data entity (e.g. files, variables, logs, configurations)
    in the ontology graph.
    """
    entity_id: str
    name: str
    entity_type: str  # e.g., 'file', 'symbol', 'constraint', 'parameter'
    properties: Dict[str, Any] = Field(default_factory=dict)
