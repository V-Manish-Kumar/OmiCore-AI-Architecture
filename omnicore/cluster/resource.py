from pydantic import BaseModel

class ResourceRequirement(BaseModel):
    """
    Requested resources for scheduling and running a task node.
    """
    cpu_cores: float = 0.5
    memory_mb: float = 128.0
    gpu_count: int = 0

class ResourceState(BaseModel):
    """
    Capacity and active allocations of cluster worker resource limits.
    """
    total_cpu_cores: float = 4.0
    total_memory_mb: float = 4096.0
    total_gpu_count: int = 0

    allocated_cpu_cores: float = 0.0
    allocated_memory_mb: float = 0.0
    allocated_gpu_count: int = 0

    @property
    def free_cpu(self) -> float:
        return max(0.0, self.total_cpu_cores - self.allocated_cpu_cores)

    @property
    def free_memory(self) -> float:
        return max(0.0, self.total_memory_mb - self.allocated_memory_mb)

    @property
    def free_gpu(self) -> int:
        return max(0, self.total_gpu_count - self.allocated_gpu_count)

    def has_capacity_for(self, req: ResourceRequirement) -> bool:
        """Checks if there are sufficient unallocated resources to run the requirement."""
        return (
            self.free_cpu >= req.cpu_cores and
            self.free_memory >= req.memory_mb and
            self.free_gpu >= req.gpu_count
        )

    def allocate(self, req: ResourceRequirement) -> None:
        self.allocated_cpu_cores += req.cpu_cores
        self.allocated_memory_mb += req.memory_mb
        self.allocated_gpu_count += req.gpu_count

    def release(self, req: ResourceRequirement) -> None:
        self.allocated_cpu_cores = max(0.0, self.allocated_cpu_cores - req.cpu_cores)
        self.allocated_memory_mb = max(0.0, self.allocated_memory_mb - req.memory_mb)
        self.allocated_gpu_count = max(0, self.allocated_gpu_count - req.gpu_count)
