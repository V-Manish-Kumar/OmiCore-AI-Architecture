from omnicore.models.cached_plan import CachedPlan
from omnicore.memory.exceptions import VersionMismatchError

COMPILER_VERSION = "1.0.0"
OPTIMIZER_VERSION = "1.0.0"

def is_compatible(plan: CachedPlan) -> bool:
    """
    Checks if a cached execution plan is compatible with the current
    compiler and optimizer configurations.
    """
    return (
        plan.compiler_version == COMPILER_VERSION and 
        plan.optimizer_version == OPTIMIZER_VERSION
    )

def validate_version(plan: CachedPlan) -> None:
    """
    Raises a VersionMismatchError if a plan is incompatible.
    """
    if not is_compatible(plan):
        raise VersionMismatchError(
            f"Plan '{plan.plan_id}' version mismatch. "
            f"Plan: compiler={plan.compiler_version}, optimizer={plan.optimizer_version}. "
            f"Runtime: compiler={COMPILER_VERSION}, optimizer={OPTIMIZER_VERSION}."
        )
