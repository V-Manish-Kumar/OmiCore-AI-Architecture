import os
import tempfile
import pytest
from omnicore.ir.enums import Capability
from omnicore.ontology.capability import OntologyCapability
from omnicore.ontology.entity import OntologyEntity
from omnicore.ontology.tool import OntologyTool
from omnicore.ontology.task import OntologyTask
from omnicore.ontology.relationship import OntologyRelationship
from omnicore.knowledge.graph_manager import KnowledgeManager
from omnicore.knowledge.graph_store import SQLiteGraphStore, JSONGraphStore
from omnicore.knowledge.graph_builder import KnowledgeGraphBuilder
from omnicore.knowledge.exceptions import OntologyValidationError
from omnicore.knowledge.diagnostics import GraphDiagnosticSeverity

# --- Unit Tests ---

def test_entity_pronoun_resolution():
    """Verify pronoun resolution maps 'it'/'them' using verb hints and symbol recency."""
    manager = KnowledgeManager()
    
    # 1. Setup entities in graph
    file_entity = OntologyEntity(
        entity_id="report.pdf",
        name="report.pdf",
        entity_type="file",
        properties={"extension": "pdf"}
    )
    summary_entity = OntologyEntity(
        entity_id="summary",
        name="summary text",
        entity_type="symbol",
        properties={"type": "string"}
    )
    
    manager.add_entity(file_entity)
    manager.add_entity(summary_entity)
    
    # Context timeline: report.pdf was created first, then summary was generated
    symbol_context = ["report.pdf", "summary"]
    
    # Action "email it" prefers the document/file ("report.pdf")
    res1 = manager.resolve_entity("email it to user@example.com", symbol_context)
    assert res1 == "report.pdf"

    # Action "summarize it" prefers files ("report.pdf") over summary strings
    res2 = manager.resolve_entity("summarize it", symbol_context)
    assert res2 == "report.pdf"

    # Generic reference defaults to the most recent symbol matching entity/symbol rules
    res3 = manager.resolve_entity("print it", symbol_context)
    assert res3 == "summary"


def test_context_neighborhood_subgraph():
    """Verify context extractor only pulls nodes within the specified hop boundaries."""
    manager = KnowledgeManager()
    builder = KnowledgeGraphBuilder(manager.kg)
    builder.build_default_capabilities().build_capability_relationships()
    
    # Add focus task
    task = OntologyTask(
        task_id="task_1",
        user_goal="summarize web contents",
        intent="Research"
    )
    manager.kg.add_task(task)
    
    # Add relationship: task_1 requires web_search
    manager.add_relationship(OntologyRelationship(
        source_id="task_1",
        target_id=Capability.WEB_SEARCH.value,
        relation_type="requires"
    ))
    
    # Focus on "task_1" at depth=1
    ctx = manager.get_context(["task_1"], depth=1)
    
    node_ids = [n["id"] for n in ctx["nodes"]]
    # task_1 and its neighbor web_search must be included
    assert "task_1" in node_ids
    assert Capability.WEB_SEARCH.value in node_ids
    
    # Capability translation (unrelated to task_1 at depth=1) should not be included
    assert Capability.TRANSLATION.value not in node_ids


def test_sqlite_and_json_graph_stores():
    """Verify persisting and loading nodes and relationships in SQLite/JSON."""
    # 1. Test SQLite persistence
    sqlite_store = SQLiteGraphStore(":memory:")
    manager = KnowledgeManager(sqlite_store)
    
    entity = OntologyEntity(entity_id="f1", name="f1", entity_type="file")
    manager.add_entity(entity)
    
    nodes = sqlite_store.get_nodes()
    assert len(nodes) == 1
    assert nodes[0][0] == "f1"

    # 2. Test JSON persistence
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "graph_db.json")
        json_store = JSONGraphStore(json_path)
        manager_json = KnowledgeManager(json_store)
        
        manager_json.add_entity(entity)
        
        nodes_json = json_store.get_nodes()
        assert len(nodes_json) == 1
        assert nodes_json[0][0] == "f1"
        
        # Test deletion
        manager_json.kg.remove_node("f1")
        assert len(json_store.get_nodes()) == 0


def test_related_capabilities_navigation():
    """Verify traversing taxonomy paths for subcapabilities."""
    manager = KnowledgeManager()
    builder = KnowledgeGraphBuilder(manager.kg)
    builder.build_default_capabilities().build_capability_relationships()
    
    # web_search subCapabilityOf retrieval
    related = manager.related_capabilities(Capability.WEB_SEARCH)
    assert Capability.RETRIEVAL in related


def test_ontology_validation_constraints():
    """Verify that ontology violations and orphaned nodes are correctly flagged."""
    manager = KnowledgeManager()
    
    # 1. Orphan node warning
    entity = OntologyEntity(entity_id="orphan_f1", name="orphan", entity_type="file")
    manager.add_entity(entity)
    
    diagnostics = manager.validate()
    # Check that warning about orphan node is emitted
    severities = [d.severity for d in diagnostics]
    assert GraphDiagnosticSeverity.WARNING in severities

    # 2. Invalid relationship pairing raises validation error on missing nodes
    with pytest.raises(OntologyValidationError):
        manager.add_relationship(OntologyRelationship(
            source_id="orphan_f1",
            target_id="missing_node_xyz",
            relation_type="requires"
        ))

    # 3. Invalid subCapabilityOf pairing logs violation (capability -> entity)
    cap = OntologyCapability(name=Capability.WEB_SEARCH, description="search")
    manager.kg.add_capability(cap)
    
    # subCapabilityOf requires capability -> capability. Linking capability -> entity is invalid.
    manager.add_relationship(OntologyRelationship(
        source_id=Capability.WEB_SEARCH.value,
        target_id="orphan_f1",
        relation_type="subCapabilityOf"
    ))
    
    diagnostics2 = manager.validate()
    severities2 = [d.severity for d in diagnostics2]
    assert GraphDiagnosticSeverity.ONTOLOGY_VIOLATION in severities2
