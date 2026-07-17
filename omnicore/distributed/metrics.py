from typing import Dict, Any, List

class ClusterMetricsTracker:
    """
    Tracks worker utilization, task throughput, execution latency, and schedule counts.
    """
    def __init__(self):
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.retries = 0
        self.latencies: List[float] = []

    def record_completion(self, duration: float) -> None:
        self.completed_tasks += 1
        self.latencies.append(duration)

    def record_failure(self) -> None:
        self.failed_tasks += 1

    def record_retry(self) -> None:
        self.retries += 1

    def get_summary(self, active_workers: int, queue_depth: int) -> Dict[str, Any]:
        avg_latency = 0.0
        if self.latencies:
            avg_latency = sum(self.latencies) / len(self.latencies)
            
        total_runs = self.completed_tasks + self.failed_tasks
        health_score = 1.0
        if total_runs > 0:
            health_score = self.completed_tasks / total_runs

        return {
            "active_workers": active_workers,
            "queue_depth": queue_depth,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "retry_count": self.retries,
            "average_execution_latency_seconds": round(avg_latency, 3),
            "cluster_health_score": round(health_score, 4)
        }
