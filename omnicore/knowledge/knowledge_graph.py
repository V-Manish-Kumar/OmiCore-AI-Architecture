import networkx as nx
from typing import Dict, Any, List, Optional, Tuple
from omnicore.ir.enums import Capability
from omnicore.ontology.capability import OntologyCapability
from omnicore.ontology.entity import OntologyEntity
from omnicore.ontology.tool import OntologyTool
from omnicore.ontology.task import OntologyTask
from omnicore.ontology.relationship import OntologyRelationship
from omnicore.knowledge.graph_store import GraphStoreInterface
from omnicore.knowledge.exceptions import OntologyValidationError
from omnicore.knowledge.diagnostics import GraphDiagnostic, GraphDiagnosticSeverity

class KnowledgeGraph:
    """
    Wraps a NetworkX directed graph to store semantic concepts (capabilities, entities, tools, tasks).
    Synchronizes in-memory graph operations with a pluggable GraphStore.
    Enforces ontology type safety and runs diagnostic consistency checks.
    """
    def __init__(self, store: GraphStoreInterface):
        self.store = store
        self.graph = nx.DiGraph()
        self.load_from_store()

    def load_from_store(self) -> None:
        """Loads and syncs in-memory NetworkX state from the store."""
        self.graph.clear()
        
        # Load nodes
        for node_id, node_type, data in self.store.get_nodes():
            self.graph.add_node(node_id, type=node_type, properties=data.get("properties", {}), name=data.get("name", node_id))
            
        # Load relationships
        for source_id, target_id, relation_type, data in self.store.get_relationships():
            self.graph.add_edge(source_id, target_id, relation_type=relation_type, properties=data.get("properties", {}))

    def add_capability(self, capability: OntologyCapability) -> None:
        node_id = capability.name.value
        props = {"description": capability.description}
        self.store.save_node(node_id, "capability", props)
        self.graph.add_node(node_id, type="capability", name=node_id, properties=props)

    def add_entity(self, entity: OntologyEntity) -> None:
        node_id = entity.entity_id
        props = {"name": entity.name, "entity_type": entity.entity_type, "properties": entity.properties}
        self.store.save_node(node_id, "entity", props)
        self.graph.add_node(node_id, type="entity", name=entity.name, properties=entity.properties, entity_type=entity.entity_type)

    def add_tool(self, tool: OntologyTool) -> None:
        node_id = tool.name
        props = {"supported_capabilities": [c.value for c in tool.supported_capabilities], "provider": tool.provider, "properties": tool.properties}
        self.store.save_node(node_id, "tool", props)
        self.graph.add_node(node_id, type="tool", name=node_id, properties=props)

    def add_task(self, task: OntologyTask) -> None:
        node_id = task.task_id
        props = {"user_goal": task.user_goal, "intent": task.intent, "complexity": task.complexity, "properties": task.properties}
        self.store.save_node(node_id, "task", props)
        self.graph.add_node(node_id, type="task", name=node_id, properties=props)

    def add_relationship(self, relationship: OntologyRelationship) -> None:
        src = relationship.source_id
        tgt = relationship.target_id
        rel_type = relationship.relation_type

        # Verify source and target nodes exist in the graph
        if not self.graph.has_node(src):
            raise OntologyValidationError(f"Relationship source node '{src}' does not exist in graph.")
        if not self.graph.has_node(tgt):
            raise OntologyValidationError(f"Relationship target node '{tgt}' does not exist in graph.")

        props = {"properties": relationship.properties}
        self.store.save_relationship(src, tgt, rel_type, props)
        self.graph.add_edge(src, tgt, relation_type=rel_type, properties=relationship.properties)

    def remove_node(self, node_id: str) -> None:
        """Removes a node and its edges from the graph and store."""
        if self.graph.has_node(node_id):
            self.graph.remove_node(node_id)
        self.store.delete_node(node_id)

    def remove_relationship(self, source_id: str, target_id: str, relation_type: str) -> None:
        """Removes a relationship from the graph and store."""
        if self.graph.has_edge(source_id, target_id):
            # Check edge attributes if multiple relations exist (NetworkX simple DiGraph only holds one edge, 
            # so we just remove the edge)
            self.graph.remove_edge(source_id, target_id)
        self.store.delete_relationship(source_id, target_id, relation_type)

    def validate_graph(self) -> List[GraphDiagnostic]:
        """
        Runs ontology consistency validation scans over the graph.
        Checks:
        - Orphaned nodes (degree = 0)
        - Invalid relations (unsupported source/target combinations)
        - Duplicate properties
        """
        diagnostics: List[GraphDiagnostic] = []
        
        # 1. Check for orphaned nodes
        for node in self.graph.nodes():
            in_deg = self.graph.in_degree(node)
            out_deg = self.graph.out_degree(node)
            if in_deg == 0 and out_deg == 0:
                diagnostics.append(GraphDiagnostic(
                    severity=GraphDiagnosticSeverity.WARNING,
                    message=f"Found orphaned node '{node}' with no relationships.",
                    suggestion="Add dependency, references, or produces relationships."
                ))

        # 2. Check relationship pairings correctness
        # Primary relationships: requires, produces, consumes, subCapabilityOf, references
        for u, v, data in self.graph.edges(data=True):
            rel_type = data.get("relation_type", "")
            type_u = self.graph.nodes[u].get("type", "")
            type_v = self.graph.nodes[v].get("type", "")

            # Check relation constraints
            if rel_type == "subCapabilityOf" and (type_u != "capability" or type_v != "capability"):
                diagnostics.append(GraphDiagnostic(
                    severity=GraphDiagnosticSeverity.ONTOLOGY_VIOLATION,
                    message=f"Invalid 'subCapabilityOf' relation from '{u}' ({type_u}) to '{v}' ({type_v}).",
                    suggestion="Ensure both nodes are capabilities."
                ))
            elif rel_type == "requires":
                allowed_srcs = {"capability", "task", "tool"}
                allowed_tgts = {"capability"}
                if type_u not in allowed_srcs or type_v not in allowed_tgts:
                    diagnostics.append(GraphDiagnostic(
                        severity=GraphDiagnosticSeverity.ONTOLOGY_VIOLATION,
                        message=f"Invalid 'requires' relation from '{u}' ({type_u}) to '{v}' ({type_v}).",
                        suggestion="Requires relation must link from a tool/task/capability to a capability."
                    ))
            elif rel_type == "produces":
                allowed_srcs = {"task", "tool", "capability"}
                allowed_tgts = {"entity"}
                if type_u not in allowed_srcs or type_v not in allowed_tgts:
                    diagnostics.append(GraphDiagnostic(
                        severity=GraphDiagnosticSeverity.ONTOLOGY_VIOLATION,
                        message=f"Invalid 'produces' relation from '{u}' ({type_u}) to '{v}' ({type_v}).",
                        suggestion="Produces relation must link to an entity."
                    ))

        return diagnostics
