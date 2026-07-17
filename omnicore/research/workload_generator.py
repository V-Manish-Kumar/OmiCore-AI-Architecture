from typing import List
from omnicore.ir.enums import Capability
from omnicore.optimizer.optimization_context import OptimizedExecutionNode, OptimizedExecutionDAG

class WorkloadGenerator:
    """
    Utility to programmatically construct synthetic workload DAGs
    for benchmarking optimization speedups and scheduling latencies.
    """
    @staticmethod
    def generate_chain(size: int) -> OptimizedExecutionDAG:
        """Generates a sequential chain of nodes: n0 -> n1 -> n2..."""
        nodes = []
        order = []
        for i in range(size):
            node_id = f"n{i}"
            nodes.append(OptimizedExecutionNode(
                node_id=node_id,
                name=f"Chain Node {i}",
                description="desc",
                capability=Capability.WEB_SEARCH if i % 2 == 0 else Capability.SUMMARIZATION,
                input="start" if i == 0 else f"out_{i-1}",
                output=f"out_{i}"
            ))
            order.append(node_id)
        return OptimizedExecutionDAG(nodes=nodes, topological_order=order)

    @staticmethod
    def generate_parallel(width: int) -> OptimizedExecutionDAG:
        """Generates independent nodes that can execute concurrently."""
        nodes = []
        order = []
        for i in range(width):
            node_id = f"p{i}"
            nodes.append(OptimizedExecutionNode(
                node_id=node_id,
                name=f"Parallel Node {i}",
                description="desc",
                capability=Capability.WEB_SEARCH,
                input=f"in_{i}",
                output=f"out_{i}"
            ))
            order.append(node_id)
        return OptimizedExecutionDAG(nodes=nodes, topological_order=order)
