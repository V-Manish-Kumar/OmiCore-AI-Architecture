from typing import Dict, Any, List
from omnicore.ir.models import TaskIR
from omnicore.ir.enums import Capability
from omnicore.planner.heuristic_engine import CAPABILITY_PROFILES

class PlannerExecutionPredictor:
    """
    Predicts scheduling metrics, latency, memory ceilings, and execution bottlenecks.
    """
    @staticmethod
    def predict_execution(task_ir: TaskIR, enable_parallel: bool = True) -> Dict[str, Any]:
        baseline_times = []
        max_mem = 64.0
        bottlenecks = []

        # Find resource details for each capability
        for cap in task_ir.required_capabilities:
            profile = CAPABILITY_PROFILES.get(cap, CAPABILITY_PROFILES[Capability.UNKNOWN])
            baseline_times.append(profile.runtime_seconds)
            max_mem = max(max_mem, profile.memory_mb)
            
            # Bottleneck threshold: any capability taking >= 8 seconds
            if profile.runtime_seconds >= 8.0:
                bottlenecks.append(cap.value)

        # Estimate runtime with concurrency reduction heuristics
        if not baseline_times:
            est_runtime = 5.0
        elif enable_parallel:
            parallelizable = []
            sequential = []
            non_parallelizable_caps = {Capability.PDF_GENERATION, Capability.EMAIL, Capability.REPORT_GENERATION}
            
            for cap in task_ir.required_capabilities:
                profile = CAPABILITY_PROFILES.get(cap, CAPABILITY_PROFILES[Capability.UNKNOWN])
                if cap in non_parallelizable_caps:
                    sequential.append(profile.runtime_seconds)
                else:
                    parallelizable.append(profile.runtime_seconds)
            
            # Concurrency math: parallel nodes run in overlap (modeled as max duration), sequential nodes sum up
            est_runtime = (max(parallelizable) if parallelizable else 0.0) + sum(sequential)
        else:
            est_runtime = sum(baseline_times)

        # Scale with constraints Jaccard
        for constraint in task_ir.constraints:
            constraint_lower = constraint.lower()
            if any(word in constraint_lower for word in ["detailed", "accuracy", "deep"]):
                est_runtime *= 1.2

        # Round values
        est_runtime = round(est_runtime, 2)
        
        # Parallel efficiency rating
        efficiency = 1.0
        if len(task_ir.required_capabilities) > 1 and enable_parallel:
            parallel_count = len([c for c in task_ir.required_capabilities if c not in {Capability.PDF_GENERATION, Capability.EMAIL, Capability.REPORT_GENERATION}])
            efficiency = round(parallel_count / len(task_ir.required_capabilities), 2)

        return {
            "estimated_runtime": est_runtime,
            "peak_memory_mb": max_mem,
            "parallel_efficiency": efficiency,
            "bottlenecks": list(set(bottlenecks))
        }
