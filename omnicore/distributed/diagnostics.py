import time
from typing import List, Dict, Any

class ClusterDiagnostics:
    """
    Logs scheduling timeline events, bottlenecks, and worker offline warnings.
    """
    def __init__(self):
        self.timeline: List[Dict[str, Any]] = []
        self.warnings: List[str] = []

    def log_event(self, event_type: str, message: str) -> None:
        self.timeline.append({
            "timestamp": time.time(),
            "event_type": event_type,
            "message": message
        })

    def log_warning(self, message: str) -> None:
        self.warnings.append(message)
        self.log_event("WARNING", message)

    def get_report(self) -> Dict[str, Any]:
        return {
            "warnings": self.warnings,
            "timeline": self.timeline
        }
