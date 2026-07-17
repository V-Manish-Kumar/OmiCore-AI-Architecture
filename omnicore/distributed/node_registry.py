import time
from typing import Dict, List, Optional, Any
from omnicore.ir.enums import Capability
from omnicore.cluster.resource import ResourceState

class NodeRegistry:
    """
    Registry of active worker nodes, tracking their locations, resources, and last heartbeat timestamps.
    """
    def __init__(self):
        self.workers: Dict[str, Dict[str, Any]] = {}

    def register_worker(self, worker_id: str, resources: ResourceState, capabilities: List[Capability]) -> None:
        """Adds or updates a worker registration entry."""
        self.workers[worker_id] = {
            "worker_id": worker_id,
            "resources": resources,
            "capabilities": capabilities,
            "last_heartbeat": time.time(),
            "active_tasks": 0,
            "status": "online"
        }

    def unregister_worker(self, worker_id: str) -> None:
        """Removes a worker node registration."""
        if worker_id in self.workers:
            del self.workers[worker_id]

    def get_worker(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves details for a single worker."""
        return self.workers.get(worker_id)

    def list_active_workers(self) -> List[str]:
        """Returns IDs of all currently online/active workers."""
        return [wid for wid, w in self.workers.items() if w["status"] == "online"]

    def clear(self) -> None:
        """Clears the registry."""
        self.workers.clear()
