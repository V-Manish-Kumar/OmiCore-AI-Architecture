import sys
import os
import json

# Ensure the root package directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omnicore.ontology.entity import OntologyEntity
from omnicore.ontology.relationship import OntologyRelationship
from omnicore.knowledge.graph_manager import KnowledgeManager
from omnicore.knowledge.graph_builder import KnowledgeGraphBuilder
from omnicore.knowledge.exceptions import OntologyValidationError
from omnicore.ir.enums import Capability

def main():
    print("=" * 80)
    print("OMNICORE KNOWLEDGE GRAPH & CONTEXT ENGINE SHOWCASE")
    print("=" * 80)

    # 1. Initialize manager and populate standard capability graphs
    manager = KnowledgeManager()
    builder = KnowledgeGraphBuilder(manager.kg)
    builder.build_default_capabilities().build_capability_relationships()

    print(f"\n[1] Built Default Capabilities and Taxonomy Relationships:")
    query_eng = manager.query()
    capabilities = query_eng.find_nodes_by_type("capability")
    print(f"  - Registered Capabilities ({len(capabilities)} total):")
    print(f"    {', '.join(capabilities[:6])} ...")

    # Show related taxonomy hierarchy
    related = manager.related_capabilities(Capability.WEB_SEARCH)
    print(f"  - Related taxonomy for '{Capability.WEB_SEARCH.value}':")
    print(f"    Depends on / Sub-capability of: {[r.value for r in related]}")

    # 2. Add domain entities to graph
    report_file = OntologyEntity(
        entity_id="report.pdf",
        name="report.pdf",
        entity_type="file",
        properties={"size_bytes": 1048576, "owner": "admin"}
    )
    summary_string = OntologyEntity(
        entity_id="summary_result",
        name="summary_result",
        entity_type="symbol",
        properties={"type": "string"}
    )
    
    manager.add_entity(report_file)
    manager.add_entity(summary_string)
    print(f"\n[2] Registered Domain Entities:")
    print("  - report.pdf (type='file')")
    print("  - summary_result (type='symbol')")

    # 3. Resolve referencing pronouns using chronological context
    symbol_history = ["report.pdf", "summary_result"]
    print(f"\n[3] Pronoun Entity Resolution:")
    print(f"  Chronological Context: {symbol_history}")
    
    # "Email it" action prefers files
    resolved_email = manager.resolve_entity("email it to admin@example.com", symbol_history)
    print(f"  - Query: \"email it\" -> Resolved to: {resolved_email} (preferred file)")

    # "Print it" defaults to recency
    resolved_print = manager.resolve_entity("print it", symbol_history)
    print(f"  - Query: \"print it\" -> Resolved to: {resolved_print} (preferred recency)")

    # 4. Context Subgraph neighborhood extraction
    print(f"\n[4] Local Context Subgraph Retrieval (focus node = '{Capability.WEB_SEARCH.value}'):")
    context = manager.get_context([Capability.WEB_SEARCH.value], depth=1)
    print("  - Context Nodes:")
    for n in context["nodes"]:
        print(f"    * {n['id']} (type={n['type']})")
    print("  - Context Edges:")
    for e in context["edges"]:
        print(f"    * {e['source']} --[{e['relation_type']}]--> {e['target']}")

    # 5. Semantic validation warnings (Diagnostics)
    print(f"\n[5] Graph Diagnostic Consistency Validation:")
    # Add an orphan entity node
    orphan = OntologyEntity(entity_id="orphan_config.json", name="orphan", entity_type="file")
    manager.add_entity(orphan)
    
    diagnostics = manager.validate()
    for d in diagnostics:
        print(f"  [{d.severity.value}] {d.message}")
        if d.suggestion:
            print(f"    Suggestion: {d.suggestion}")

    # 6. Test invalid relationship exception handling
    print(f"\n[6] Invalid Relationship Enforcement:")
    try:
        manager.add_relationship(OntologyRelationship(
            source_id="report.pdf",
            target_id="nonexistent_target_node",
            relation_type="requires"
        ))
    except OntologyValidationError as e:
        print(f"  - Caught Expected Exception: {e}")

if __name__ == "__main__":
    main()
