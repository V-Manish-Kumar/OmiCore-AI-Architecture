import networkx as nx
from typing import List, Set, Dict, Any

class GraphQueryEngine:
    """
    Supplies path search and traversal query capabilities over a NetworkX Knowledge Graph.
    """
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def find_shortest_path(self, source: str, target: str) -> List[str]:
        """Finds the shortest directed path of node IDs from source to target."""
        try:
            return list(nx.shortest_path(self.graph, source, target))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def get_ancestors(self, node: str) -> Set[str]:
        """Returns all ancestor node IDs that can reach the given node."""
        if not self.graph.has_node(node):
            return set()
        return nx.ancestors(self.graph, node)

    def get_descendants(self, node: str) -> Set[str]:
        """Returns all descendant node IDs reachable from the given node."""
        if not self.graph.has_node(node):
            return set()
        return nx.descendants(self.graph, node)

    def get_neighbors(self, node: str) -> List[str]:
        """Returns immediate successor and predecessor node IDs of a node."""
        if not self.graph.has_node(node):
            return []
        # Return all connected node IDs (both in-edges and out-edges)
        return list(set(self.graph.successors(node)).union(set(self.graph.predecessors(node))))

    def find_nodes_by_type(self, node_type: str) -> List[str]:
        """Finds all node IDs in the graph matching the specified ontology type."""
        return [
            nid for nid, attr in self.graph.nodes(data=True) 
            if attr.get("type") == node_type
        ]
