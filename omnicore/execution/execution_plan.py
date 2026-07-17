import uuid
from typing import List, Dict
from pydantic import BaseModel, Field, ConfigDict
from omnicore.ir.models import Dependency
from omnicore.optimizer.optimization_context import OptimizedExecutionNode, OptimizedExecutionDAG
from omnicore.execution.execution_stage import ExecutionStage

class ExecutionPlan(BaseModel):
    """
    Combines the optimized DAG and scheduling properties into an executable plan structure.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:8]}")
    stages: List[ExecutionStage] = Field(default_factory=list)
    topological_order: List[str] = Field(default_factory=list)
    nodes: Dict[str, OptimizedExecutionNode] = Field(default_factory=dict)
    dependencies: List[Dependency] = Field(default_factory=list)

    @classmethod
    def from_dag(cls, dag: OptimizedExecutionDAG) -> "ExecutionPlan":
        """Factory method to construct an ExecutionPlan from an OptimizedExecutionDAG."""
        stages = []
        for idx, stage_nodes in enumerate(dag.stages):
            stages.append(ExecutionStage(stage_index=idx, node_ids=stage_nodes))
        
        node_dict = {n.node_id: n for n in dag.nodes}
        
        return cls(
            stages=stages,
            topological_order=list(dag.topological_order),
            nodes=node_dict,
            dependencies=list(dag.dependencies)
        )
