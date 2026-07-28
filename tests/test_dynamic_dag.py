import pytest
from omnicore.parser.intent_parser import IntentParser
from omnicore.ast.ast_parser import ASTParser
from omnicore.ir.enums import Capability

def test_dynamic_dag_pdf_research_query():
    parser = IntentParser()
    query = "create a pdf that contains information of ML tools search google for research"
    task_ir, dag = parser.compile(query)

    assert task_ir is not None
    assert dag is not None
    
    # Verify that the generated DAG contains all 4 required execution nodes:
    # 1. Web Search Node
    # 2. Data Analysis Node
    # 3. Summarization Node
    # 4. PDF Generation Node
    assert len(dag.nodes) >= 4

    capabilities = [node.capability for node in dag.nodes]
    assert Capability.WEB_SEARCH in capabilities
    assert Capability.DATA_ANALYSIS in capabilities
    assert Capability.SUMMARIZATION in capabilities
    assert Capability.PDF_GENERATION in capabilities

    # Check topological ordering and dependencies
    assert len(dag.topological_order) == len(dag.nodes)
    
    search_idx = next(i for i, node in enumerate(dag.nodes) if node.capability == Capability.WEB_SEARCH)
    analysis_idx = next(i for i, node in enumerate(dag.nodes) if node.capability == Capability.DATA_ANALYSIS)
    summary_idx = next(i for i, node in enumerate(dag.nodes) if node.capability == Capability.SUMMARIZATION)
    pdf_idx = next(i for i, node in enumerate(dag.nodes) if node.capability == Capability.PDF_GENERATION)

    search_id = dag.nodes[search_idx].node_id
    analysis_id = dag.nodes[analysis_idx].node_id
    summary_id = dag.nodes[summary_idx].node_id
    pdf_id = dag.nodes[pdf_idx].node_id

    search_topo = dag.topological_order.index(search_id)
    analysis_topo = dag.topological_order.index(analysis_id)
    summary_topo = dag.topological_order.index(summary_id)
    pdf_topo = dag.topological_order.index(pdf_id)

    assert search_topo < analysis_topo
    assert analysis_topo < summary_topo
    assert summary_topo < pdf_topo

def test_dynamic_dag_research_report_query():
    parser = IntentParser()
    query = "research python web frameworks and write a pdf summary"
    task_ir, dag = parser.compile(query)

    assert len(dag.nodes) >= 3
    capabilities = [node.capability for node in dag.nodes]
    assert Capability.WEB_SEARCH in capabilities
    assert Capability.SUMMARIZATION in capabilities
    assert Capability.PDF_GENERATION in capabilities
