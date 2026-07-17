from typing import List
from omnicore.ir.models import ExecutionDAG, Dependency
from omnicore.optimizer.optimization_context import OptimizedExecutionDAG, OptimizedExecutionNode

def build_dag_from_graph(graph_nodes: List[OptimizedExecutionNode], dependencies: List[Dependency], topological_order: List[str]) -> OptimizedExecutionDAG:
    """Helper function to instantiate an OptimizedExecutionDAG model."""
    return OptimizedExecutionDAG(
        nodes=graph_nodes,
        dependencies=dependencies,
        topological_order=topological_order
    )
