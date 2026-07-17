from typing import List, Dict, Any, Optional
from omnicore.ast.ast_nodes import ProgramAST
from omnicore.compiler.symbol_table import SymbolTable

class CompilationContext:
    """
    Holds the state of the compiler throughout the compilation passes.
    """
    def __init__(self, raw_input: str, ast: ProgramAST):
        self.raw_input = raw_input
        self.ast = ast
        self.symbol_table = SymbolTable()
        self.metadata: Dict[str, Any] = {}
        self.task_ir: Any = None          # Populated by IRLoweringPass
        self.execution_dag: Any = None    # Populated by DAGLoweringPass
        self.errors: List[str] = []       # Diagnostic/validation errors
        self.warnings: List[str] = []     # Warnings/heuristics notes

    def has_errors(self) -> bool:
        return len(self.errors) > 0


class BasePass:
    """
    Base class for all compiler passes.
    """
    def run(self, context: CompilationContext) -> None:
        raise NotImplementedError("Pass must implement the run method.")


class PassManager:
    """
    Manages registration and execution of compiler passes.
    """
    def __init__(self):
        self.passes: List[BasePass] = []

    def add_pass(self, compiler_pass: BasePass) -> None:
        """
        Registers a compiler pass.
        """
        self.passes.append(compiler_pass)

    def run(self, context: CompilationContext) -> CompilationContext:
        """
        Executes all registered passes sequentially.
        """
        for compiler_pass in self.passes:
            # Run pass
            compiler_pass.run(context)
            # If critical errors are found, we halt the pass manager pipeline
            if context.has_errors():
                break
        return context
