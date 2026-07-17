import math
from typing import List, Dict

class StatisticalAnalyst:
    """
    Computes statistical indicators for benchmark metrics:
    Mean, Median, Standard Deviation, Percentiles, and Confidence intervals.
    """
    @staticmethod
    def calculate_stats(values: List[float]) -> Dict[str, float]:
        """Calculates statistical summary for a list of runs."""
        if not values:
            return {
                "mean": 0.0, "median": 0.0, "stddev": 0.0,
                "p50": 0.0, "p90": 0.0, "p99": 0.0, "stderr": 0.0
            }

        sorted_vals = sorted(values)
        n = len(values)
        
        # Mean
        mean_val = sum(values) / n
        
        # Median
        if n % 2 == 1:
            median_val = sorted_vals[n // 2]
        else:
            median_val = (sorted_vals[(n // 2) - 1] + sorted_vals[n // 2]) / 2.0
            
        # Standard Deviation
        variance = sum((x - mean_val) ** 2 for x in values) / max(n - 1, 1)
        stddev_val = math.sqrt(variance)
        
        # Percentiles (interpolated)
        def get_percentile(p: float) -> float:
            k = (n - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return sorted_vals[int(k)]
            return sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f])

        p50 = get_percentile(0.50)
        p90 = get_percentile(0.90)
        p99 = get_percentile(0.99)
        
        # Standard Error of the Mean
        stderr_val = stddev_val / math.sqrt(n)

        return {
            "mean": round(mean_val, 5),
            "median": round(median_val, 5),
            "stddev": round(stddev_val, 5),
            "p50": round(p50, 5),
            "p90": round(p90, 5),
            "p99": round(p99, 5),
            "stderr": round(stderr_val, 5)
        }
