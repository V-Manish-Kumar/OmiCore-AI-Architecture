import time
import asyncio
from typing import Dict, List, Any
from omnicore.research.experiment_config import ExperimentConfig
from omnicore.optimizer.optimizer import TaskOptimizer
from omnicore.parser.intent_parser import IntentParser
from omnicore.runtime.runtime import AdaptiveRuntime
from omnicore.runtime.adapters.capability_adapter import MockCapabilityAdapter
from omnicore.optimizer.optimization_context import OptimizedExecutionDAG

class BenchmarkRunner:
    """
    Executes compilation passes and task pipelines multiple times
    to gather reproducible performance latency measurements.
    """
    def __init__(self):
        pass

    async def run_workload_async(self, config: ExperimentConfig, dag: OptimizedExecutionDAG) -> Dict[str, List[float]]:
        """
        Runs compilation and execution workloads repeatedly in an async context,
        recording elapsed times in seconds.
        """
        parse_times = []
        opt_times = []
        exec_times = []

        parser = IntentParser()
        optimizer = TaskOptimizer()
        adapter = MockCapabilityAdapter(latency=0.01)
        runtime = AdaptiveRuntime(adapter=adapter)

        # Mock query string matching size
        query = "Search " * config.workload_size

        for _ in range(config.runs_count):
            # 1. Parse Phase
            t0 = time.perf_counter()
            task_ir, raw_dag = parser.compile(query)
            parse_times.append(time.perf_counter() - t0)

            # 2. Optimize Phase
            t1 = time.perf_counter()
            opt_dag, report = optimizer.optimize(task_ir, raw_dag)
            opt_times.append(time.perf_counter() - t1)

            # 3. Execution Phase
            t2 = time.perf_counter()
            await runtime.execute(opt_dag, inputs={"query": "test"})
            exec_times.append(time.perf_counter() - t2)

        return {
            "parsing": parse_times,
            "optimization": opt_times,
            "execution": exec_times
        }

    def run_workload(self, config: ExperimentConfig, dag: OptimizedExecutionDAG) -> Dict[str, List[float]]:
        """Synchronous wrapper for run_workload_async."""
        return asyncio.run(self.run_workload_async(config, dag))
