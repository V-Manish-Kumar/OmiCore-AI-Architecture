from typing import List, Type
from pydantic import BaseModel, Field
from omnicore.runtime.exceptions import PermanentNodeError

class RetryPolicy(BaseModel):
    """
    Configurable policy managing task retry limits and backoff calculations.
    """
    max_retries: int = 3
    base_delay: float = 0.1
    max_delay: float = 5.0
    backoff_factor: float = 2.0
    retryable_exceptions: List[str] = Field(default_factory=list)

    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """
        Determines whether a task should be retried based on failure count
        and error type. PermanentNodeErrors are never retried.
        """
        if attempt >= self.max_retries:
            return False
            
        if isinstance(exception, PermanentNodeError):
            return False
            
        # If no explicit list is provided, default to retrying all exceptions
        if not self.retryable_exceptions:
            return True
            
        exc_name = exception.__class__.__name__
        return exc_name in self.retryable_exceptions

    def get_delay(self, attempt: int) -> float:
        """Calculates backoff delay for the given retry attempt (1-indexed)."""
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))
        return min(delay, self.max_delay)
