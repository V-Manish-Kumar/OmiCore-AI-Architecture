from omnicore.cluster.resource import ResourceRequirement
from omnicore.distributed.node_registry import NodeRegistry
from omnicore.distributed.exceptions import WorkerNotFoundError

class ResourceManager:
    """
    Manages resource allocations, capacity validations, and task counts across cluster workers.
    """
    def __init__(self, registry: NodeRegistry):
        self.registry = registry

    def has_resources(self, worker_id: str, requirement: ResourceRequirement) -> bool:
        """Checks if a worker has enough free resources."""
        worker = self.registry.get_worker(worker_id)
        if not worker:
            raise WorkerNotFoundError(f"Worker '{worker_id}' not found in registry.")
        return worker["resources"].has_capacity_for(requirement)

    def allocate_resources(self, worker_id: str, requirement: ResourceRequirement) -> None:
        """Allocates resources on a worker node and increments its task count."""
        worker = self.registry.get_worker(worker_id)
        if not worker:
            raise WorkerNotFoundError(f"Worker '{worker_id}' not found in registry.")
        worker["resources"].allocate(requirement)
        worker["active_tasks"] += 1

    def release_resources(self, worker_id: str, requirement: ResourceRequirement) -> None:
        """Releases allocated resources on a worker node and decrements its task count."""
        worker = self.registry.get_worker(worker_id)
        if not worker:
            return
        worker["resources"].release(requirement)
        worker["active_tasks"] = max(0, worker["active_tasks"] - 1)
