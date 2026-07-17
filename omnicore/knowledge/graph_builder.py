from omnicore.ir.enums import Capability
from omnicore.ontology.capability import OntologyCapability
from omnicore.ontology.relationship import OntologyRelationship
from omnicore.knowledge.knowledge_graph import KnowledgeGraph

class KnowledgeGraphBuilder:
    """
    Fluent builder class to populate the Knowledge Graph with standard
    capabilities, tool mappings, and relationship taxonomies.
    """
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg

    def build_default_capabilities(self) -> "KnowledgeGraphBuilder":
        """Registers all Capability enums with the graph."""
        caps = [
            (Capability.WEB_SEARCH, "Retrieves information from internet search engines."),
            (Capability.CODE_GENERATION, "Generates software source code."),
            (Capability.SUMMARIZATION, "Condenses long text inputs into summaries."),
            (Capability.COMPARISON, "Compares multiple sets of data items."),
            (Capability.TRANSLATION, "Translates texts between natural languages."),
            (Capability.REASONING, "Executes logical reasoning, problem-solving, and chain of thought."),
            (Capability.RETRIEVAL, "Fetches data resources and local file assets."),
            (Capability.REPORT_GENERATION, "Generates reports, documentation, or charts."),
            (Capability.EMAIL, "Dispatches emails and notifications."),
            (Capability.PDF_GENERATION, "Compiles PDF document binaries from text/summaries."),
            (Capability.DATABASE_ACCESS, "Executes database queries, reads, and writes."),
            (Capability.UNKNOWN, "Generic undefined capability slot.")
        ]
        
        for cap, desc in caps:
            self.kg.add_capability(OntologyCapability(name=cap, description=desc))
            
        return self

    def build_capability_relationships(self) -> "KnowledgeGraphBuilder":
        """Registers default taxonomy hierarchies and capability dependencies."""
        # e.g., web_search is a subCapability of general retrieval
        # pdf_generation is a subCapability of report_generation
        relations = [
            (Capability.WEB_SEARCH.value, Capability.RETRIEVAL.value, "subCapabilityOf"),
            (Capability.PDF_GENERATION.value, Capability.REPORT_GENERATION.value, "subCapabilityOf"),
            (Capability.REPORT_GENERATION.value, Capability.SUMMARIZATION.value, "requires"),
            (Capability.CODE_GENERATION.value, Capability.REASONING.value, "requires")
        ]
        
        for src, tgt, rel in relations:
            self.kg.add_relationship(OntologyRelationship(
                source_id=src,
                target_id=tgt,
                relation_type=rel
            ))
            
        return self
