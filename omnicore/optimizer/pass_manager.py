import time
from typing import List, Dict, Any, Optional
from omnicore.optimizer.optimization_context import OptimizerState, Diagnostic, DiagnosticSeverity
from omnicore.optimizer.exceptions import ValidationError

class BaseOptimizerPass:
    """
    Abstract base class for all optimizer pipeline passes.
    """
    def run(self, state: OptimizerState) -> OptimizerState:
        raise NotImplementedError("Passes must implement the run method.")


class PassManager:
    """
    Compiler-style pipeline manager for optimization passes.
    Manages pass registration, pipeline sequencing, timing, and diagnostic collection.
    """
    def __init__(self):
        self._registered_passes: Dict[str, BaseOptimizerPass] = {}
        self._pipeline_order: List[str] = []
        self._disabled_passes: set[str] = set()
        
        # Execution statistics
        self._pass_durations: Dict[str, float] = {}
        self._execution_count: int = 0

    def register_pass(self, name: str, pass_inst: BaseOptimizerPass) -> None:
        """Registers a pass instance with a unique name."""
        self._registered_passes[name] = pass_inst

    def add_pass_to_pipeline(self, name: str) -> None:
        """Appends a registered pass name to the active pipeline execution order."""
        if name not in self._registered_passes:
            raise ValueError(f"Pass '{name}' must be registered before adding to pipeline.")
        if name not in self._pipeline_order:
            self._pipeline_order.append(name)

    def set_pipeline_order(self, order: List[str]) -> None:
        """Sets or reconfigures the sequence of passes in the pipeline."""
        for name in order:
            if name not in self._registered_passes:
                raise ValueError(f"Pass '{name}' is not registered.")
        self._pipeline_order = list(order)

    def enable_pass(self, name: str) -> None:
        """Enables a pass if it was previously disabled."""
        self._disabled_passes.discard(name)

    def disable_pass(self, name: str) -> None:
        """Disables a pass from execution without removing it from the pipeline."""
        self._disabled_passes.add(name)

    def run(self, state: OptimizerState) -> OptimizerState:
        """
        Runs the active pipeline passes in order.
        If a pass produces fatal errors (DiagnosticSeverity.ERROR), execution terminates.
        """
        current_state = state
        self._pass_durations.clear()
        self._execution_count += 1

        for pass_name in self._pipeline_order:
            if pass_name in self._disabled_passes:
                continue

            pass_inst = self._registered_passes[pass_name]
            
            # Run pass and measure duration
            start_time = time.perf_counter()
            current_state = pass_inst.run(current_state)
            duration = time.perf_counter() - start_time
            
            self._pass_durations[pass_name] = duration
            
            # Record that this pass was executed
            passes_run = list(current_state.passes_run) + [pass_name]
            current_state = current_state.model_copy(update={"passes_run": passes_run})

            # Check for fatal errors in diagnostics
            has_fatal = any(d.severity == DiagnosticSeverity.ERROR for d in current_state.diagnostics)
            if has_fatal:
                # Halt pipeline immediately on validation/fatal errors
                errors = [d.message for d in current_state.diagnostics if d.severity == DiagnosticSeverity.ERROR]
                raise ValidationError(errors)

        return current_state

    def get_statistics(self) -> Dict[str, Any]:
        """Returns performance and execution statistics of the passes."""
        return {
            "total_execution_runs": self._execution_count,
            "pass_durations_seconds": self._pass_durations,
            "total_pipeline_time_seconds": sum(self._pass_durations.values()),
            "active_pipeline": [p for p in self._pipeline_order if p not in self._disabled_passes],
            "disabled_passes": list(self._disabled_passes)
        }
