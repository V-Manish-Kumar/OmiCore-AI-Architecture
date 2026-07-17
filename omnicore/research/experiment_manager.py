from typing import Dict, Any
from omnicore.research.experiment_config import ExperimentConfig
from omnicore.research.workload_generator import WorkloadGenerator
from omnicore.research.benchmark_runner import BenchmarkRunner
from omnicore.research.statistical_analysis import StatisticalAnalyst

class ExperimentManager:
    """
    Coordinates execution of workloads across multiple runs, aggregating
    timings and computing statistical summaries.
    """
    def __init__(self):
        self.runner = BenchmarkRunner()

    def run_experiment(self, config: ExperimentConfig) -> Dict[str, Any]:
        """
        Runs experiment: generates workload, executes benchmarks, and computes stats.
        """
        # 1. Generate workload DAG
        if config.workload_type == "parallel":
            dag = WorkloadGenerator.generate_parallel(config.workload_size)
        else:
            dag = WorkloadGenerator.generate_chain(config.workload_size)

        # 2. Run benchmarks
        raw_metrics = self.runner.run_workload(config, dag)

        # 3. Analyze statistics
        results = {}
        for phase, timings in raw_metrics.items():
            results[phase] = StatisticalAnalyst.calculate_stats(timings)

        return {
            "config": config.model_dump(),
            "metrics": results,
            "raw_timings": raw_metrics
        }
