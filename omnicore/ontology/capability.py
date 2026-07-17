from pydantic import BaseModel
from omnicore.ir.enums import Capability

class OntologyCapability(BaseModel):
    """
    Semantic definition of a compiler capability in the ontology graph.
    """
    name: Capability
    description: str
