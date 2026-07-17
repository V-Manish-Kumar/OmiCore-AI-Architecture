import time
from typing import Dict, Any

class MemoryMetricsTracker:
    """
    Tracks cache retrieval speed, reuse metrics, and compiler speedups.
    """
    def __init__(self):
        self.retrieval_times: list[float] = []
        self.plan_reuse_count: int = 0
        self.total_optimization_savings: float = 0.0

    def record_retrieval(self, duration: float) -> None:
        """Records the time taken to query/retrieve plans."""
        self.retrieval_times.append(duration)

    def record_reuse(self, time_saved: float = 0.05) -> None:
        """Increments the reuse counter and adds compilation time savings."""
        self.plan_reuse_count += 1
        self.total_optimization_savings += time_saved

    def get_summary(self) -> Dict[str, Any]:
        """Returns the summary dictionary of memory performance metrics."""
        avg_retrieval = 0.0
        if self.retrieval_times:
            avg_retrieval = sum(self.retrieval_times) / len(self.retrieval_times)
            
        return {
            "average_retrieval_time_seconds": round(avg_retrieval, 6),
            "plan_reuse_frequency": self.plan_reuse_count,
            "total_optimization_savings_seconds": round(self.total_optimization_savings, 4)
        }
