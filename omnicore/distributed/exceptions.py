class ClusterError(ValueError):
    """Base exception for all distributed clustering errors."""
    pass

class ResourceExhaustedError(ClusterError):
    """Raised when cluster resources are insufficient to schedule task nodes."""
    pass

class WorkerNotFoundError(ClusterError):
    """Raised when a task targets a worker node that does not exist or has timed out."""
    pass
