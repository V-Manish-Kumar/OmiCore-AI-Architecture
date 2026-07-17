from typing import List, Dict
from omnicore.optimizer.pass_manager import BaseOptimizerPass
from omnicore.optimizer.optimization_context import (
    OptimizerState,
    Diagnostic,
    DiagnosticSeverity,
    OptimizationReport
)

class OptimizationReportPass(BaseOptimizerPass):
    """
    Pass 8: Generates a structured optimization report from compilation state.
    Exposes metrics for node counts, parallel groups, critical path, resources, and diagnostics.
    """
    def run(self, state: OptimizerState) -> OptimizerState:
        dag = state.execution_dag

        # Collect warning messages specifically
        warnings = [d.message for d in state.diagnostics if d.severity == DiagnosticSeverity.WARNING]

        # Extract stats from metadata
        removed = state.metadata.get("removed_nodes", [])
        merged = state.metadata.get("merged_nodes", {})
        parallel_groups = state.metadata.get("parallel_groups", [])

        # Determine original nodes (fall back to current nodes + removed if not set)
        current_node_ids = [n.node_id for n in dag.nodes]
        original_nodes = state.metadata.get("original_nodes", list(current_node_ids) + list(removed))

        report = OptimizationReport(
            original_nodes=original_nodes,
            optimized_nodes=current_node_ids,
            removed_nodes=list(removed),
            merged_nodes=dict(merged),
            parallel_groups=parallel_groups,
            critical_path=list(dag.critical_path),
            estimated_runtime=dag.estimated_runtime,
            estimated_cost=dag.estimated_cost,
            estimated_tokens=dag.estimated_tokens,
            optimization_passes_applied=list(state.passes_run) + ["optimization_report"],
            warnings=warnings,
            compiler_diagnostics=list(state.diagnostics)
        )

        # Save the report in the state metadata
        new_metadata = {**state.metadata, "optimization_report": report}

        return state.model_copy(update={"metadata": new_metadata})
