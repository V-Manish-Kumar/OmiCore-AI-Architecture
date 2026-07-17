import time
from typing import Dict, List, Any

class RuntimeMetricsTracker:
    """
    Collects and computes performance and run statistics for adaptive executions.
    """
    def __init__(self):
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        
        # Node stats
        self.node_durations: Dict[str, float] = {}
        self.node_start_times: Dict[str, float] = {}
        self.execution_order: List[str] = []
        
        # Concurrency & Retry counts
        self.total_retries: int = 0
        self.peak_parallelism: int = 0
        self._current_parallelism: int = 0

    def start_runtime(self) -> None:
        """Starts timing the overall runtime execution."""
        self.start_time = time.perf_counter()

    def finish_runtime(self) -> None:
        """Stops timing the overall runtime execution."""
        self.end_time = time.perf_counter()

    def record_node_start(self, node_id: str) -> None:
        """Records node startup, updating execution order and parallelism tracking."""
        now = time.perf_counter()
        self.node_start_times[node_id] = now
        self.execution_order.append(node_id)
        
        self._current_parallelism += 1
        if self._current_parallelism > self.peak_parallelism:
            self.peak_parallelism = self._current_parallelism

    def record_node_finish(self, node_id: str) -> None:
        """Records node completion and calculates its duration."""
        now = time.perf_counter()
        self._current_parallelism -= 1
        
        if node_id in self.node_start_times:
            duration = now - self.node_start_times[node_id]
            self.node_durations[node_id] = duration

    def record_node_cancelled_or_failed(self, node_id: str) -> None:
        """Updates parallelism tracking if a node fails or is cancelled."""
        self._current_parallelism = max(0, self._current_parallelism - 1)

    def record_retry(self) -> None:
        """Increments the global retry counter."""
        self.total_retries += 1

    def get_summary(self, total_nodes: int, completed_nodes: int) -> Dict[str, Any]:
        """Computes and returns the execution metrics summary dictionary."""
        total_time = 0.0
        if self.start_time > 0:
            total_time = (self.end_time or time.perf_counter()) - self.start_time
            
        success_rate = (completed_nodes / total_nodes) if total_nodes > 0 else 0.0
        
        return {
            "total_runtime_seconds": round(total_time, 4),
            "node_execution_durations": {nid: round(dur, 4) for nid, dur in self.node_durations.items()},
            "success_rate": round(success_rate, 4),
            "total_retries": self.total_retries,
            "peak_parallelism": self.peak_parallelism,
            "execution_order": list(self.execution_order)
        }
