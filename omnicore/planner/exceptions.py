class PlannerError(ValueError):
    """Base exception for all planning subsystem errors."""
    pass

class PlanningException(PlannerError):
    """Raised when the planning subsystem fails to compile a plan."""
    pass
