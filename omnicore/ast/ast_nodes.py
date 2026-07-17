from typing import List, Optional, Union
from pydantic import BaseModel, Field

class ASTNode(BaseModel):
    """Base class for all AST nodes."""
    pass

class ParameterNode(ASTNode):
    """Represents a parameter extracted from the natural language (e.g. limit=5)."""
    name: str
    value: str

class CommandNode(ASTNode):
    """Represents an individual task command or step (e.g., 'Search GitHub for Python compiler projects')."""
    raw_text: str
    action_verb: str
    target: str
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    parameters: List[ParameterNode] = Field(default_factory=list)

class ConjunctionNode(ASTNode):
    """Represents concurrent execution (e.g. A and B, in parallel)."""
    left: ASTNode
    right: ASTNode

class SequenceNode(ASTNode):
    """Represents sequential execution (e.g. A, then B, in order)."""
    left: ASTNode
    right: ASTNode

class ProgramAST(ASTNode):
    """The root of the Abstract Syntax Tree representation of a query."""
    root: ASTNode
    global_constraints: List[str] = Field(default_factory=list)
