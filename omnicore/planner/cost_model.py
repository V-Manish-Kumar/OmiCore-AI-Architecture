from typing import Dict, Any
from omnicore.ir.models import TaskIR
from omnicore.ir.enums import Capability
from omnicore.planner.heuristic_engine import CAPABILITY_PROFILES

class PlannerCostModel:
    """
    Estimates token counts and costs based on required capabilities and constraints.
    """
    COST_PER_TOKEN = 0.00002
    SEARCH_FLAT_COST = 0.01

    @staticmethod
    def estimate_resources(task_ir: TaskIR) -> Dict[str, Any]:
        total_tokens = 0
        total_cost = 0.0
        
        # 1. Sum up baseline resources for required capabilities
        for cap in task_ir.required_capabilities:
            profile = CAPABILITY_PROFILES.get(cap, CAPABILITY_PROFILES[Capability.UNKNOWN])
            total_tokens += profile.token_usage
            
            # API pricing
            cost = profile.token_usage * PlannerCostModel.COST_PER_TOKEN
            if cap == Capability.WEB_SEARCH:
                cost += PlannerCostModel.SEARCH_FLAT_COST
            total_cost += cost

        # 2. Scale according to constraints (e.g. detailed research increases complexity)
        scale_factor = 1.0
        for constraint in task_ir.constraints:
            constraint_lower = constraint.lower()
            if any(word in constraint_lower for word in ["detailed", "accuracy", "deep", "extensive", "academic"]):
                scale_factor *= 1.3
            elif any(word in constraint_lower for word in ["brief", "short", "fast", "simple"]):
                scale_factor *= 0.8

        final_tokens = int(total_tokens * scale_factor)
        final_cost = round(total_cost * scale_factor, 4)

        return {
            "estimated_tokens": final_tokens,
            "estimated_cost": final_cost
        }
