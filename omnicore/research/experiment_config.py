from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ExperimentConfig(BaseModel):
    """
    Pydantic parameters defining compiler configuration, scheduling policies,
    runs counts, random seed, and hardware metadata for reproducibility.
    """
    experiment_name: str
    random_seed: int = 42
    runs_count: int = 5
    scheduler_policy: str = "least_loaded"
    optimization_passes: List[str] = Field(default_factory=lambda: [
        "validation", "capability_resolution", "dependency_analysis", "parallelization"
    ])
    hardware_metadata: Dict[str, Any] = Field(default_factory=dict)
    workload_type: str = "chain"  # chain, tree, parallel
    workload_size: int = 3
