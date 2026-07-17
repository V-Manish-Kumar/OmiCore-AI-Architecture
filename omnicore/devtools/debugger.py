from typing import Dict, Any, Callable, Set, Optional

class CompilerDebugger:
    """
    Compiler debugger allowing step-through breakpoints after compiler phases
    (parsing, validation, optimization, scheduling).
    Invokes register breakpoint handlers and exposes intermediate compilation states.
    """
    def __init__(self):
        self.breakpoints: Set[str] = set()
        self.breakpoint_handler: Optional[Callable[[str, Any], None]] = None
        self.execution_state: Dict[str, Any] = {}

    def set_breakpoint(self, phase: str) -> None:
        """Sets a breakpoint at a specific compiler phase."""
        self.breakpoints.add(phase)

    def remove_breakpoint(self, phase: str) -> None:
        """Removes a breakpoint at a specific compiler phase."""
        self.breakpoints.discard(phase)

    def step(self, phase: str, state: Any) -> None:
        """
        Triggered by the compiler after completing a phase.
        If a breakpoint is set, invokes the handler callback.
        """
        self.execution_state[phase] = state
        if phase in self.breakpoints and self.breakpoint_handler:
            # Pause and trigger breakpoint callback
            self.breakpoint_handler(phase, state)
