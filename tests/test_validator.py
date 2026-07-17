import pytest
from omnicore.parser.intent_parser import IntentParser, CompileError
from omnicore.compiler.pass_manager import CompilationContext
from omnicore.ast.ast_nodes import ProgramAST, CommandNode, SequenceNode
from omnicore.compiler.passes import (
    SymbolResolutionPass,
    IRLoweringPass,
    DAGLoweringPass,
)

def test_validation_detects_dataflow_cycle():
    # Construct a cycle:
    # Summarize reports using the comparison, and compare reports using the summary.
    # summarize_1 (input: comparison, output: summary)
    # compare_1 (input: summary, output: comparison)
    parser = IntentParser()
    
    query = (
        "Summarize the comparison to generate a summary, "
        "then compare repositories using the summary to generate a comparison."
    )
    
    # Let's verify if compile raises CompileError due to cycle
    with pytest.raises(CompileError) as excinfo:
        parser.compile(query)
    
    assert "cycle" in str(excinfo.value).lower()

def test_validation_detects_direct_cycle():
    # Manually configure a context with a cycle and run DAG Lowering Pass
    # Node A -> Node B -> Node A
    ast = ProgramAST(
        root=SequenceNode(
            left=CommandNode(raw_text="A", action_verb="search", target="A", inputs=["input_a"], outputs=["output_a"]),
            right=CommandNode(raw_text="B", action_verb="compare", target="B", inputs=["input_b"], outputs=["output_b"])
        ),
        global_constraints=[]
    )
    context = CompilationContext("raw input", ast)
    
    # Run symbol resolution to assign IDs (A will be search_1, B will be compare_1)
    SymbolResolutionPass().run(context)
    IRLoweringPass().run(context)
    
    # Let's manually inject a cycle into the Symbol Table
    # search_1 consumes 'output_b' (which is produced by compare_1)
    # compare_1 consumes 'output_a' (which is produced by search_1)
    context.symbol_table.insert("output_a", "data", producer_node_id="search_1")
    context.symbol_table.add_consumer("output_a", "compare_1")
    
    context.symbol_table.insert("output_b", "data", producer_node_id="compare_1")
    context.symbol_table.add_consumer("output_b", "search_1")
    
    # Run DAG Lowering
    DAGLoweringPass().run(context)
    
    assert context.has_errors()
    assert any("cycle detected" in err.lower() for err in context.errors)
