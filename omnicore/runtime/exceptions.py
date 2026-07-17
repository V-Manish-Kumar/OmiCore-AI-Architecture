class RuntimeException(Exception):
    """Base exception for all runtime-related errors."""
    pass

class NodeExecutionError(RuntimeException):
    """Raised when execution of a node fails."""
    def __init__(self, node_id: str, message: str, original_exception: Exception = None):
        self.node_id = node_id
        self.original_exception = original_exception
        super().__init__(f"Node '{node_id}' failed: {message}")

class PermanentNodeError(RuntimeException):
    """Raised when a node encounters a permanent/non-retryable failure."""
    def __init__(self, node_id: str, message: str):
        self.node_id = node_id
        super().__init__(f"Permanent error in node '{node_id}': {message}")

class CheckpointError(RuntimeException):
    """Raised when serialization or deserialization of execution state fails."""
    pass
