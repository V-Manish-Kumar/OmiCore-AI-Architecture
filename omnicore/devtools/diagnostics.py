from typing import Optional, List
from pydantic import BaseModel

class CompilerDiagnostic(BaseModel):
    """
    Structured warning/diagnostic log generated during compilation stages.
    """
    severity: str  # Warning, Note, Suggestion, RiskAssessment
    category: str
    phase: str
    message: str
    affected_node: Optional[str] = None
    suggested_fix: Optional[str] = None

class ObservabilityDiagnostics:
    """
    Registry for gathering and querying devtools compiler warnings and issues.
    """
    def __init__(self):
        self.reports: List[CompilerDiagnostic] = []

    def log_diagnostic(self, diag: CompilerDiagnostic) -> None:
        self.reports.append(diag)

    def list_warnings(self) -> List[CompilerDiagnostic]:
        return [r for r in self.reports if r.severity == "Warning"]

    def clear(self) -> None:
        self.reports.clear()
