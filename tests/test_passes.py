from omnicore.ast.ast_parser import ASTParser
from omnicore.compiler.pass_manager import CompilationContext
from omnicore.compiler.passes import (
    SymbolResolutionPass,
    ClassifierPass,
    CapabilityConstraintPass,
    IRLoweringPass,
    DAGLoweringPass,
)
from omnicore.ir.enums import TaskIntent, Capability, Complexity

def test_classifier_pass():
    parser = ASTParser()
    ast = parser.parse("Search python compiler projects and program a backend")
    context = CompilationContext("Search python compiler projects and program a backend", ast)
    
    pass_obj = ClassifierPass()
    pass_obj.run(context)
    
    assert context.metadata["primary_intent"] in (TaskIntent.PROGRAMMING, TaskIntent.RESEARCH)
    assert context.metadata["domain"] in ("Software Engineering", "Academic/Market Research")

def test_capability_constraint_pass():
    parser = ASTParser()
    ast = parser.parse("Search python compiler projects in PDF format")
    context = CompilationContext("Search python compiler projects in PDF format", ast)
    
    # Needs Symbol Resolution first to set up node_metadata
    SymbolResolutionPass().run(context)
    CapabilityConstraintPass().run(context)
    
    assert Capability.WEB_SEARCH in context.metadata["required_capabilities"]
    assert "Output must be PDF format" in context.metadata["constraints"]

def test_ir_lowering_pass():
    parser = ASTParser()
    ast = parser.parse("Search python compiler projects")
    context = CompilationContext("Search python compiler projects", ast)
    
    SymbolResolutionPass().run(context)
    ClassifierPass().run(context)
    CapabilityConstraintPass().run(context)
    IRLoweringPass().run(context)
    
    assert context.task_ir is not None
    assert context.task_ir.primary_intent in (TaskIntent.RESEARCH, TaskIntent.PROGRAMMING, TaskIntent.UNKNOWN)
    assert context.task_ir.estimated_complexity == Complexity.SIMPLE
