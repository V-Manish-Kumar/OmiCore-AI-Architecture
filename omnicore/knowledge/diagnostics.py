from enum import Enum
from typing import Optional
from pydantic import BaseModel

class GraphDiagnosticSeverity(str, Enum):
    WARNING = "Warning"
    NOTE = "Note"
    SUGGESTION = "Suggestion"
    ONTOLOGY_VIOLATION = "OntologyViolation"

class GraphDiagnostic(BaseModel):
    """
    Diagnostic report for Knowledge Graph consistency checks.
    """
    severity: GraphDiagnosticSeverity
    message: str
    suggestion: Optional[str] = None
