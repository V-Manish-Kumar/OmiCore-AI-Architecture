class DevToolsError(ValueError):
    """Base exception for all DevTools and observability errors."""
    pass

class DebuggerException(DevToolsError):
    """Raised when debugger breakpoint stepping errors occur."""
    pass
