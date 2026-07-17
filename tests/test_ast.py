from omnicore.ast.ast_nodes import ProgramAST, CommandNode, SequenceNode, ConjunctionNode
from omnicore.ast.ast_parser import ASTParser

def test_empty_query():
    parser = ASTParser()
    ast = parser.parse("")
    assert isinstance(ast, ProgramAST)
    assert isinstance(ast.root, CommandNode)
    assert ast.root.action_verb == "noop"

def test_simple_query():
    parser = ASTParser()
    ast = parser.parse("Search Python compiler projects")
    assert isinstance(ast, ProgramAST)
    assert isinstance(ast.root, CommandNode)
    assert ast.root.action_verb == "search"
    assert ast.root.target == "Python compiler projects"

def test_sequenced_query():
    parser = ASTParser()
    ast = parser.parse("Search Python compiler projects then write a report")
    assert isinstance(ast, ProgramAST)
    assert isinstance(ast.root, SequenceNode)
    assert isinstance(ast.root.left, CommandNode)
    assert isinstance(ast.root.right, CommandNode)
    assert ast.root.left.action_verb == "search"
    assert ast.root.right.action_verb == "write"

def test_conjunction_query():
    parser = ASTParser()
    ast = parser.parse("Search Python compiler projects while generating code in parallel")
    assert isinstance(ast, ProgramAST)
    assert isinstance(ast.root, ConjunctionNode)
    assert isinstance(ast.root.left, CommandNode)
    assert isinstance(ast.root.right, CommandNode)
    assert ast.root.left.action_verb == "search"
    assert ast.root.right.action_verb == "generate"
