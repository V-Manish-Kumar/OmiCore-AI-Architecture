class OptimizerError(ValueError):
    """Base exception for all optimization-related errors."""
    pass

class ValidationError(OptimizerError):
    """Raised when the input task IR or execution graph fails validation checks."""
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__(f"Validation failed with {len(errors)} error(s): {'; '.join(errors)}")

class CycleError(ValidationError):
    """Raised when a dependency cycle is detected in the execution graph."""
    pass
