from typing import Dict, Any
from pydantic import BaseModel, Field

class OntologyRelationship(BaseModel):
    """
    Semantic definition of a directed relationship link between ontology elements.
    """
    source_id: str
    target_id: str
    relation_type: str  # e.g., 'produces', 'consumes', 'requires', 'subCapabilityOf', 'references'
    properties: Dict[str, Any] = Field(default_factory=dict)
