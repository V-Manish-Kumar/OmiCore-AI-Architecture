import networkx as nx
from typing import List, Dict, Any

class ContextEngine:
    """
    Extracts relevant context subgraphs (focused neighborhoods) from the global Knowledge Graph.
    """
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def get_context(self, focus_nodes: List[str], depth: int = 1) -> Dict[str, Any]:
        """
        Pulls a neighborhood subgraph of diameter 'depth' around focus_nodes.
        Returns a dictionary of relevant nodes and relationships.
        """
        # Validate node existences
        valid_focus = [n for n in focus_nodes if self.graph.has_node(n)]
        if not valid_focus:
            return {"nodes": [], "edges": []}

        # Find all nodes within 'depth' undirected steps from any focus node
        neighborhood_nodes = set(valid_focus)
        for _ in range(depth):
            current_nodes = list(neighborhood_nodes)
            for node in current_nodes:
                # Add successors (outgoing) and predecessors (incoming)
                successors = self.graph.successors(node)
                predecessors = self.graph.predecessors(node)
                neighborhood_nodes.update(successors)
                neighborhood_nodes.update(predecessors)

        # Build induced subgraph
        subgraph = self.graph.subgraph(neighborhood_nodes)

        # Format output
        nodes_list = []
        for nid, attrs in subgraph.nodes(data=True):
            nodes_list.append({
                "id": nid,
                "type": attrs.get("type"),
                "name": attrs.get("name"),
                "properties": attrs.get("properties", {})
            })

        edges_list = []
        for u, v, data in subgraph.edges(data=True):
            edges_list.append({
                "source": u,
                "target": v,
                "relation_type": data.get("relation_type"),
                "properties": data.get("properties", {})
            })

        return {
            "nodes": nodes_list,
            "edges": edges_list
        }
