from omnicore.ir.models import TaskIR
from omnicore.ir.enums import Capability

class PlacementStrategy:
    """
    Decides load balancer policies based on execution constraints and capability properties.
    """
    @staticmethod
    def get_policy(task_ir: TaskIR) -> str:
        # 1. Resource intensive capability goes Resource-Aware
        heavy_caps = {Capability.REASONING, Capability.CODE_GENERATION}
        if heavy_caps.intersection(set(task_ir.required_capabilities)):
            return "resource_aware"

        # 2. Fast/Low-latency constraints go Round Robin
        constraints_str = " ".join(task_ir.constraints).lower()
        if any(w in constraints_str for w in ["fast", "speed", "realtime"]):
            return "round_robin"

        # 3. Default is Least Loaded
        return "least_loaded"
