from typing import List, Optional
from omnicore.ir.models import ExecutionDAG, ExecutionNode, Dependency
from omnicore.graph.execution_graph import ExecutionGraph

class GraphBuilder:
    """
    Builder utility to construct ExecutionGraph instances.
    """
    @staticmethod
    def build_from_dag(dag: ExecutionDAG) -> ExecutionGraph:
        """Constructs an ExecutionGraph from a Pydantic ExecutionDAG."""
        return ExecutionGraph(nodes=dag.nodes, dependencies=dag.dependencies)

    @staticmethod
    def build_from_nodes_and_deps(
        nodes: List[ExecutionNode], 
        dependencies: List[Dependency]
    ) -> ExecutionGraph:
        """Constructs an ExecutionGraph from lists of nodes and dependency models."""
        return ExecutionGraph(nodes=nodes, dependencies=dependencies)
