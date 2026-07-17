from enum import Enum
from typing import Optional
from pydantic import BaseModel

class PlannerDiagnosticSeverity(str, Enum):
    WARNING = "Warning"
    NOTE = "Note"
    SUGGESTION = "Suggestion"
    RISK_ASSESSMENT = "RiskAssessment"

class PlannerDiagnostic(BaseModel):
    """
    Diagnostics reports, warnings, suggestions, and risks output by the planner.
    """
    severity: PlannerDiagnosticSeverity
    message: str
    suggestion: Optional[str] = None
