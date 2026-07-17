import time
import asyncio
from typing import Callable, Optional
from omnicore.communication.message_bus import LocalMessageBus
from omnicore.communication.serializer import Serializer
from omnicore.communication.protocol import HeartbeatMessage
from omnicore.distributed.node_registry import NodeRegistry

class HeartbeatMonitor:
    """
    Subscribes to heartbeat messages and marks silent workers offline.
    """
    def __init__(
        self, 
        registry: NodeRegistry, 
        bus: LocalMessageBus, 
        timeout_seconds: float = 3.0,
        on_worker_failed_callback: Optional[Callable[[str], None]] = None
    ):
        self.registry = registry
        self.bus = bus
        self.timeout_seconds = timeout_seconds
        self.on_worker_failed = on_worker_failed_callback
        self.is_running = False
        self._monitor_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Starts background heartbeat monitor listener and sweep loop."""
        self.is_running = True
        self.bus.subscribe("worker_heartbeats", self._receive_heartbeat)
        self._monitor_task = asyncio.create_task(self._sweep_loop())

    async def stop(self) -> None:
        """Stops background sweeps."""
        self.is_running = False
        self.bus.unsubscribe("worker_heartbeats", self._receive_heartbeat)
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

    async def _receive_heartbeat(self, msg_str: str) -> None:
        """Processes a received worker heartbeat message."""
        try:
            msg = Serializer.deserialize(msg_str, HeartbeatMessage)
            worker = self.registry.get_worker(msg.worker_id)
            if worker:
                worker["last_heartbeat"] = time.time()
                # Recover worker if it was offline
                if worker["status"] == "offline":
                    worker["status"] = "online"
        except Exception:
            pass

    async def _sweep_loop(self) -> None:
        """Periodic sweep loop checking for worker heartbeat timeouts."""
        while self.is_running:
            try:
                await asyncio.sleep(0.05)
                now = time.time()
                for wid in list(self.registry.workers.keys()):
                    worker = self.registry.get_worker(wid)
                    if worker and worker["status"] == "online":
                        elapsed = now - worker["last_heartbeat"]
                        # print(f"[DEBUG] Worker {wid} elapsed: {elapsed:.3f}s")
                        if elapsed > self.timeout_seconds:
                            print(f"[DEBUG] Worker {wid} timed out! Switching to offline.")
                            worker["status"] = "offline"
                            if self.on_worker_failed:
                                self.on_worker_failed(wid)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[DEBUG] Sweep error: {e}")
