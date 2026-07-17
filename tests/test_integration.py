from omnicore.parser.intent_parser import IntentParser
from omnicore.ir.enums import TaskIntent, Capability, Complexity

def test_end_to_end_compilation():
    parser = IntentParser()
    query = (
        "Search GitHub for Python compiler projects, compare the top five repositories, "
        "summarize the findings, and generate a PDF."
    )
    
    task_ir, execution_dag = parser.compile(query)
    
    # Assert IR fields
    assert task_ir.task_id.startswith("task_")
    assert task_ir.primary_intent in (TaskIntent.PROGRAMMING, TaskIntent.RESEARCH)
    assert task_ir.domain == "Software Engineering"
    assert "Output must be PDF format" in task_ir.constraints
    assert len(task_ir.required_capabilities) == 4
    
    # Assert DAG nodes
    assert len(execution_dag.nodes) == 4
    node_ids = [n.node_id for n in execution_dag.nodes]
    assert "search_1" in node_ids
    assert "compare_1" in node_ids
    assert "summarize_1" in node_ids
    assert "generate_1" in node_ids
    
    # Assert DAG topological order
    assert execution_dag.topological_order == ["search_1", "compare_1", "summarize_1", "generate_1"]
    
    # Assert dependencies exist
    assert len(execution_dag.dependencies) >= 3
    dep_tuples = [dep.to_tuple() for dep in execution_dag.dependencies]
    assert ("summarize_1", "generate_1") in dep_tuples
