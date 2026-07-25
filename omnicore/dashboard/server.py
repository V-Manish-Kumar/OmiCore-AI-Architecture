import uvicorn
import threading
import time
from typing import Optional
from omnicore.dashboard.api import app

class DashboardServer:
    """
    Observability web dashboard server running FastAPI/Uvicorn on a background thread.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8001):
        self.host = host
        self.port = port
        self._thread: Optional[threading.Thread] = None
        self._server: Optional[uvicorn.Server] = None

    def start(self) -> None:
        """Starts the Uvicorn web server in a daemonized background thread."""
        config = uvicorn.Config(
            app=app, 
            host=self.host, 
            port=self.port, 
            log_level="warning",
            loop="asyncio"
        )
        self._server = uvicorn.Server(config)
        
        self._thread = threading.Thread(
            target=self._server.run, 
            daemon=True,
            name="OmniCoreDashboardThread"
        )
        self._thread.start()
        # Give the server a moment to spin up and bind
        time.sleep(0.5)

    def stop(self) -> None:
        """Stops the running Uvicorn server gracefully."""
        if self._server:
            self._server.should_exit = True
            if self._thread:
                self._thread.join(timeout=2.0)
            self._server = None
            self._thread = None

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)

