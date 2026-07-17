from typing import List, Optional
from omnicore.ir.enums import Capability
from omnicore.cluster.resource import ResourceRequirement
from omnicore.distributed.node_registry import NodeRegistry
from omnicore.distributed.exceptions import WorkerNotFoundError, ResourceExhaustedError

class LoadBalancer:
    """
    Distributes tasks to workers according to balancing strategies (RoundRobin, LeastLoaded, ResourceAware).
    """
    def __init__(self, registry: NodeRegistry):
        self.registry = registry
        self.rr_index = 0

    def select_worker(
        self, 
        capability: Capability, 
        requirement: ResourceRequirement, 
        policy: str = "least_loaded"
    ) -> str:
        """
        Chooses an online worker node supporting the capability under the balancing policy.
        """
        active_ids = self.registry.list_active_workers()
        if not active_ids:
            raise WorkerNotFoundError("No active worker nodes found in cluster.")

        # Filter workers by supported capability
        candidates = []
        for wid in active_ids:
            worker = self.registry.get_worker(wid)
            if worker and capability in worker["capabilities"]:
                candidates.append(worker)

        if not candidates:
            raise WorkerNotFoundError(f"No active worker node supports capability '{capability.value}'.")

        # Policy 1: Resource Aware (only keep candidates with enough capacity, then sort by free resources)
        if policy == "resource_aware":
            capable_candidates = [
                w for w in candidates 
                if w["resources"].has_capacity_for(requirement)
            ]
            if not capable_candidates:
                raise ResourceExhaustedError(
                    f"Resource capacity exceeded. No worker has enough capacity "
                    f"for task requiring: CPU={requirement.cpu_cores}, Mem={requirement.memory_mb}MB."
                )
            # Sort by free CPU descending
            capable_candidates.sort(key=lambda w: w["resources"].free_cpu, reverse=True)
            return capable_candidates[0]["worker_id"]

        # Policy 2: Round Robin
        if policy == "round_robin":
            worker = candidates[self.rr_index % len(candidates)]
            self.rr_index += 1
            return worker["worker_id"]

        # Policy 3: Least Loaded (default)
        # Sort by active_tasks ascending
        candidates.sort(key=lambda w: w["active_tasks"])
        return candidates[0]["worker_id"]
