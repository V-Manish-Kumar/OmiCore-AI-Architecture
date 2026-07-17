from typing import Dict, Any

class ComparisonEngine:
    """
    Compares two benchmark execution runs to identify latency speedups
    and optimization pass impacts.
    """
    @staticmethod
    def compare_experiments(run_a: Dict[str, Any], run_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compares results of Run A (e.g. Baseline) against Run B (e.g. Optimized).
        Computes speedup percentage: (MeanA - MeanB) / MeanA * 100
        """
        comparisons = {}
        metrics_a = run_a.get("metrics", {})
        metrics_b = run_b.get("metrics", {})

        for phase in ["parsing", "optimization", "execution"]:
            phase_a = metrics_a.get(phase, {})
            phase_b = metrics_b.get(phase, {})
            
            mean_a = phase_a.get("mean", 0.0)
            mean_b = phase_b.get("mean", 0.0)

            speedup_pct = 0.0
            if mean_a > 0:
                speedup_pct = ((mean_a - mean_b) / mean_a) * 100.0

            comparisons[phase] = {
                "mean_a": mean_a,
                "mean_b": mean_b,
                "speedup_percentage": round(speedup_pct, 2)
            }

        return {
            "config_a": run_a.get("config", {}).get("experiment_name"),
            "config_b": run_b.get("config", {}).get("experiment_name"),
            "comparisons": comparisons
        }
