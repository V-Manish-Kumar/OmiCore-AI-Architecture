import asyncio

class CancellationToken:
    """
    Cooperative cancellation token to propagate cancellation requests across runtime workers.
    """
    def __init__(self):
        self._event = asyncio.Event()

    def cancel(self) -> None:
        """Requests cancellation."""
        self._event.set()

    @property
    def is_cancelled(self) -> bool:
        """Returns True if cancellation has been requested."""
        return self._event.is_set()

    def throw_if_cancelled(self) -> None:
        """Raises asyncio.CancelledError if cancellation was requested."""
        if self.is_cancelled:
            raise asyncio.CancelledError("Runtime execution cancellation requested.")

    async def wait(self) -> None:
        """Blocks asynchronously until cancellation is requested."""
        await self._event.wait()
