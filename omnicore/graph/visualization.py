from omnicore.graph.execution_graph import ExecutionGraph

def export_to_dot(graph: ExecutionGraph, title: str = "Execution DAG") -> str:
    """Exports the execution graph to Graphviz DOT representation."""
    return graph.to_dot(title)
