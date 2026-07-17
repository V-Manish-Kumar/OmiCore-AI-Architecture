from typing import Tuple, List, Dict, Any
from omnicore.ast.ast_parser import ASTParser
from omnicore.compiler.pass_manager import PassManager, CompilationContext
from omnicore.compiler.passes import (
    SymbolResolutionPass,
    ClassifierPass,
    CapabilityConstraintPass,
    IRLoweringPass,
    DAGLoweringPass,
)
from omnicore.ir.models import TaskIR, ExecutionDAG

class CompileError(ValueError):
    """
    Exception raised when compilation or validation fails.
    """
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(f"Compilation failed with {len(errors)} error(s): {'; '.join(errors)}")


class IntentParser:
    """
    Orchestrates the entire compiler front-end: Lexing, Parsing AST,
    resolving symbols, running compilation passes, lowering, and DAG validation.
    """
    def __init__(self):
        self.ast_parser = ASTParser()
        self.pass_manager = PassManager()
        # Initialize default compilation pipeline passes
        self.pass_manager.add_pass(SymbolResolutionPass())
        self.pass_manager.add_pass(ClassifierPass())
        self.pass_manager.add_pass(CapabilityConstraintPass())
        self.pass_manager.add_pass(IRLoweringPass())
        self.pass_manager.add_pass(DAGLoweringPass())

    def compile(self, text: str) -> Tuple[TaskIR, ExecutionDAG]:
        """
        Compiles the given natural language instruction into (TaskIR, ExecutionDAG).
        Raises CompileError if errors are encountered in compilation or validation.
        """
        # Step 1: Parse AST
        ast = self.ast_parser.parse(text)

        # Step 2: Initialize Compilation Context
        context = CompilationContext(raw_input=text, ast=ast)

        # Step 3: Run compiler passes
        self.pass_manager.run(context)

        # Step 4: Validate errors
        if context.has_errors():
            raise CompileError(context.errors)

        return context.task_ir, context.execution_dag
