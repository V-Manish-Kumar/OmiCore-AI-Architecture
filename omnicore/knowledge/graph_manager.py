from typing import List, Dict, Any, Optional
from omnicore.ir.enums import Capability
from omnicore.ontology.entity import OntologyEntity
from omnicore.ontology.relationship import OntologyRelationship
from omnicore.knowledge.knowledge_graph import KnowledgeGraph
from omnicore.knowledge.graph_store import GraphStoreInterface, SQLiteGraphStore
from omnicore.knowledge.graph_query import GraphQueryEngine
from omnicore.knowledge.entity_resolver import EntityResolver
from omnicore.knowledge.relationship_engine import RelationshipEngine
from omnicore.knowledge.context_engine import ContextEngine
from omnicore.knowledge.diagnostics import GraphDiagnostic

class KnowledgeManager:
    """
    High-level orchestration API manager for the Knowledge Graph and Context Engine.
    Exposes direct methods for graph manipulation, diagnostics, context extraction,
    and semantic symbol pronoun resolution.
    """
    def __init__(self, store: Optional[GraphStoreInterface] = None):
        self.store = store or SQLiteGraphStore()
        self.kg = KnowledgeGraph(self.store)
        
        # Engines
        self.query_engine = GraphQueryEngine(self.kg.graph)
        self.resolver = EntityResolver(self.kg.graph)
        self.relation_engine = RelationshipEngine(self.kg.graph)
        self.context_engine = ContextEngine(self.kg.graph)

    def add_entity(self, entity: OntologyEntity) -> None:
        """Saves a semantic entity node to the graph and store."""
        self.kg.add_entity(entity)

    def add_relationship(self, relationship: OntologyRelationship) -> None:
        """Saves a directed relationship link to the graph and store."""
        self.kg.add_relationship(relationship)

    def query(self) -> GraphQueryEngine:
        """Returns the traversal query engine interface."""
        # Refresh reference to dynamic networkx graph state
        self.query_engine.graph = self.kg.graph
        return self.query_engine

    def get_context(self, focus_nodes: List[str], depth: int = 1) -> Dict[str, Any]:
        """Pulls a relevant neighborhood context subgraph."""
        self.context_engine.graph = self.kg.graph
        return self.context_engine.get_context(focus_nodes, depth)

    def resolve_entity(self, query: str, symbol_context: List[str]) -> Optional[str]:
        """Resolves pronouns ('it', 'them') to concrete symbols in context."""
        self.resolver.graph = self.kg.graph
        return self.resolver.resolve_reference(query, symbol_context)

    def related_capabilities(self, capability: Capability) -> List[Capability]:
        """Finds taxonomical capabilities connected in the graph."""
        self.relation_engine.graph = self.kg.graph
        return self.relation_engine.related_capabilities(capability)

    def validate(self) -> List[GraphDiagnostic]:
        """Scans the graph for orphans and ontology constraint violations."""
        return self.kg.validate_graph()

    def clear(self) -> None:
        """Deletes all nodes and edges from memory and store."""
        self.kg.graph.clear()
        self.store.clear()
