class MemoryError(ValueError):
    """Base exception for all procedural memory errors."""
    pass

class StorageError(MemoryError):
    """Raised when storage operations fail."""
    pass

class VersionMismatchError(MemoryError):
    """Raised when a plan is incompatible due to version changes."""
    pass
