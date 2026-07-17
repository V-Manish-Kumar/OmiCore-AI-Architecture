import time
from typing import Dict, Any, List

class PerformanceProfiler:
    """
    Measures processing duration of compiler phases, planner scheduling latencies,
    and caching hit ratios. Generates detailed profiler reports.
    """
    def __init__(self):
        self.phase_times: Dict[str, List[float]] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def record_phase(self, phase_name: str, duration_seconds: float) -> None:
        """Records time spent in a specific compiler/runtime phase."""
        if phase_name not in self.phase_times:
            self.phase_times[phase_name] = []
        self.phase_times[phase_name].append(duration_seconds)

    def record_cache_hit(self) -> None:
        self.cache_hits += 1

    def record_cache_miss(self) -> None:
        self.cache_misses += 1

    def get_performance_report(self) -> Dict[str, Any]:
        """Compiles a detailed performance profiling report."""
        averages = {}
        for phase, times in self.phase_times.items():
            averages[f"average_{phase}_seconds"] = round(sum(times) / len(times), 4) if times else 0.0

        total_cache = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_cache) if total_cache > 0 else 0.0

        return {
            "phase_metrics": averages,
            "caching": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_rate": round(hit_rate, 4)
            },
            "timestamp": time.time()
        }

    def clear(self) -> None:
        self.phase_times.clear()
        self.cache_hits = 0
        self.cache_misses = 0
