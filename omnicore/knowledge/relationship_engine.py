import networkx as nx
from typing import List
from omnicore.ir.enums import Capability

class RelationshipEngine:
    """
    Analyzes taxonomy relations (e.g. subCapabilities) and tool provider pairings.
    """
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def related_capabilities(self, capability: Capability) -> List[Capability]:
        """
        Traverses 'subCapabilityOf' and 'requires' connections to identify 
        semantically related capabilities.
        """
        cap_val = capability.value
        if not self.graph.has_node(cap_val):
            return []

        related = set()
        
        # Traverse out-edges (what this capability depends on / subCapabilityOf)
        for target in self.graph.successors(cap_val):
            edge_data = self.graph.get_edge_data(cap_val, target)
            if edge_data.get("relation_type") in ("subCapabilityOf", "requires"):
                try:
                    related.add(Capability(target))
                except ValueError:
                    pass

        # Traverse in-edges (what capabilities depend on this cap)
        for source in self.graph.predecessors(cap_val):
            edge_data = self.graph.get_edge_data(source, cap_val)
            if edge_data.get("relation_type") in ("subCapabilityOf", "requires"):
                try:
                    related.add(Capability(source))
                except ValueError:
                    pass

        return list(related)

    def get_tool_support(self, capability: Capability) -> List[str]:
        """
        Returns all tool node IDs that support the given capability.
        """
        cap_val = capability.value
        tools = []

        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("type") == "tool":
                # Check supported_capabilities property
                supported = attrs.get("properties", {}).get("supported_capabilities", [])
                if cap_val in supported:
                    tools.append(node_id)
                # Check requires relationship
                elif self.graph.has_edge(node_id, cap_val):
                    edge_data = self.graph.get_edge_data(node_id, cap_val)
                    if edge_data.get("relation_type") == "requires":
                        tools.append(node_id)

        return list(set(tools))
