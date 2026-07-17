import networkx as nx
from typing import List, Dict, Any, Optional, Tuple, Set
from omnicore.ir.models import ExecutionNode, Dependency

class ExecutionGraph:
    """
    Wraps a NetworkX directed graph representation of execution nodes and dependency edges.
    Provides algorithms for analysis, scheduling, critical path, and staging.
    """
    def __init__(self, nodes: Optional[List[ExecutionNode]] = None, dependencies: Optional[List[Dependency]] = None):
        self.graph = nx.DiGraph()
        self._node_lookup: Dict[str, ExecutionNode] = {}
        
        if nodes:
            for node in nodes:
                self.add_node(node)
        if dependencies:
            for dep in dependencies:
                self.add_dependency(dep.source, dep.target)

    def add_node(self, node: ExecutionNode) -> None:
        """Adds a node to the execution graph."""
        self._node_lookup[node.node_id] = node
        # Store the node object as a node attribute in NetworkX
        self.graph.add_node(node.node_id, obj=node)

    def add_dependency(self, source_id: str, target_id: str) -> None:
        """Adds a directed dependency edge from source to target."""
        self.graph.add_edge(source_id, target_id)

    def remove_node(self, node_id: str) -> None:
        """Removes a node and all of its associated edges from the graph."""
        if node_id in self._node_lookup:
            del self._node_lookup[node_id]
        if self.graph.has_node(node_id):
            self.graph.remove_node(node_id)

    def has_node(self, node_id: str) -> bool:
        """Checks if a node ID exists in the graph."""
        return self.graph.has_node(node_id)

    def get_node(self, node_id: str) -> Optional[ExecutionNode]:
        """Looks up a node object by its ID."""
        return self._node_lookup.get(node_id)

    def get_all_nodes(self) -> List[ExecutionNode]:
        """Returns all execution node objects."""
        return list(self._node_lookup.values())

    def get_dependencies(self) -> List[Dependency]:
        """Returns all dependency edges as Dependency models."""
        return [Dependency(source=u, target=v) for u, v in self.graph.edges()]

    def has_cycle(self) -> bool:
        """Returns True if the execution graph contains directed cycles."""
        return not nx.is_directed_acyclic_graph(self.graph)

    def find_cycle(self) -> List[Tuple[str, str]]:
        """Finds and returns a cycle as a list of edges, if one exists."""
        try:
            return list(nx.find_cycle(self.graph))
        except nx.NetworkXNoCycle:
            return []

    def topological_sort(self) -> List[str]:
        """Returns a topological sorting of the node IDs."""
        if self.has_cycle():
            return []
        return list(nx.topological_sort(self.graph))

    def get_successors(self, node_id: str) -> List[str]:
        """Returns the immediate successors (consumers) of the given node ID."""
        if not self.graph.has_node(node_id):
            return []
        return list(self.graph.successors(node_id))

    def get_predecessors(self, node_id: str) -> List[str]:
        """Returns the immediate predecessors (producers) of the given node ID."""
        if not self.graph.has_node(node_id):
            return []
        return list(self.graph.predecessors(node_id))

    def critical_path(self) -> List[str]:
        """
        Calculates the critical path of the DAG (the path of node IDs with the maximum
        cumulative estimated time).
        """
        if self.has_cycle() or not self._node_lookup:
            return []

        order = self.topological_sort()
        
        # dist[u] stores the max cumulative time from any source to u
        dist: Dict[str, float] = {}
        parent: Dict[str, Optional[str]] = {}
        
        # Initialize
        for node_id in order:
            node = self._node_lookup[node_id]
            dist[node_id] = node.estimated_time or 0.0
            parent[node_id] = None

        # Relax edges in topological order
        for u in order:
            u_node = self._node_lookup[u]
            u_time = u_node.estimated_time or 0.0
            for v in self.graph.successors(u):
                v_node = self._node_lookup[v]
                v_time = v_node.estimated_time or 0.0
                if dist[u] + v_time > dist[v]:
                    dist[v] = dist[u] + v_time
                    parent[v] = u

        if not dist:
            return []

        # Find the node that has the maximum distance (sink of critical path)
        end_node = max(dist.keys(), key=lambda k: dist[k])
        
        # Reconstruct path backwards
        path = []
        curr = end_node
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
            
        path.reverse()
        return path

    def generate_execution_stages(self) -> List[List[str]]:
        """
        Generates parallel execution stages.
        All nodes in a stage can run in parallel because they have no dependencies on each other.
        """
        if self.has_cycle():
            return []

        stages: List[List[str]] = []
        # Copy graph to destructively process in Kahn's level-by-level structure
        g = self.graph.copy()
        
        while g.nodes():
            # Find all nodes with 0 in-degree in the current sub-graph
            zero_in_degree = [node for node, degree in g.in_degree() if degree == 0]
            if not zero_in_degree:
                # If there are nodes remaining but no 0 in-degree, a cycle exists (should not happen since we checked)
                break
            # Sort node IDs for deterministic scheduling output
            zero_in_degree.sort()
            stages.append(zero_in_degree)
            g.remove_nodes_from(zero_in_degree)

        return stages

    def to_dot(self, title: str = "Execution DAG") -> str:
        """
        Exports the graph to Graphviz DOT format for visualization.
        """
        dot_lines = [f"digraph {repr(title)} {{", '  rankdir="LR";', "  node [shape=box, style=filled, fillcolor=lightblue, fontname=Helvetica];"]
        
        # Add nodes with metadata labels
        for node_id in self.topological_sort():
            node = self._node_lookup[node_id]
            time_str = f"{node.estimated_time}s" if node.estimated_time else "0s"
            cap_str = node.capability.value
            label = f"{node_id}\\n({cap_str})\\n{time_str}"
            dot_lines.append(f'  "{node_id}" [label="{label}"];')
            
        # Add dependency edges
        for u, v in self.graph.edges():
            dot_lines.append(f'  "{u}" -> "{v}";')
            
        dot_lines.append("}")
        return "\n".join(dot_lines)
