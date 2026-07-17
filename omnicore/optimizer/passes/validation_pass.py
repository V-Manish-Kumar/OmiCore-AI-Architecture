from typing import List, Dict, Set
from omnicore.optimizer.pass_manager import BaseOptimizerPass
from omnicore.optimizer.optimization_context import OptimizerState, Diagnostic, DiagnosticSeverity
from omnicore.optimizer.exceptions import ValidationError, CycleError
from omnicore.ir.enums import Capability
from omnicore.graph.execution_graph import ExecutionGraph

class ValidationPass(BaseOptimizerPass):
    """
    Pass 1: Validates the Task IR and Execution DAG for errors.
    Checks:
    - Invalid node definitions
    - Duplicate node IDs
    - Invalid dependencies (missing source/target nodes)
    - Missing capabilities (e.g. Capability.UNKNOWN or required but missing)
    - Missing inputs (inputs consumed by a node but neither globally provided nor produced by a node)
    - Missing outputs (outputs globally expected but never produced)
    - Dependency cycles
    """
    def run(self, state: OptimizerState) -> OptimizerState:
        diagnostics: List[Diagnostic] = list(state.diagnostics)
        dag = state.execution_dag
        task_ir = state.task_ir
        
        # 1. Check duplicate node IDs & invalid nodes
        seen_node_ids: Set[str] = set()
        all_node_outputs: Set[str] = set()
        
        for node in dag.nodes:
            # Check invalid node structure
            if not node.node_id or not node.node_id.strip():
                diagnostics.append(Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    pass_name="ValidationPass",
                    message="Found a node with an empty or missing node_id.",
                    suggestion="Ensure all execution nodes have valid unique identifiers."
                ))
            elif node.node_id in seen_node_ids:
                diagnostics.append(Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    pass_name="ValidationPass",
                    node_id=node.node_id,
                    message=f"Duplicate node ID detected: '{node.node_id}'",
                    suggestion="Rename nodes to ensure unique identifiers."
                ))
            else:
                seen_node_ids.add(node.node_id)

            if not node.name or not node.name.strip():
                diagnostics.append(Diagnostic(
                    severity=DiagnosticSeverity.WARNING,
                    pass_name="ValidationPass",
                    node_id=node.node_id,
                    message=f"Node '{node.node_id}' has an empty name.",
                    suggestion="Add a descriptive name for readability."
                ))

            # Collect outputs for input/output verification
            node_outputs = node.output or []
            if isinstance(node_outputs, str):
                node_outputs = [node_outputs]
            for out in node_outputs:
                all_node_outputs.add(out)

            # Check missing capability / UNKNOWN capability
            if node.capability == Capability.UNKNOWN:
                diagnostics.append(Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    pass_name="ValidationPass",
                    node_id=node.node_id,
                    message=f"Node '{node.node_id}' has UNKNOWN capability.",
                    suggestion="Map the node's action to a recognized compiler capability."
                ))

        # 2. Check invalid dependencies
        for dep in dag.dependencies:
            if dep.source not in seen_node_ids:
                diagnostics.append(Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    pass_name="ValidationPass",
                    message=f"Dependency source '{dep.source}' refers to a non-existent node.",
                    suggestion="Verify dependency relationships."
                ))
            if dep.target not in seen_node_ids:
                diagnostics.append(Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    pass_name="ValidationPass",
                    message=f"Dependency target '{dep.target}' refers to a non-existent node.",
                    suggestion="Verify dependency relationships."
                ))

        # 3. Check missing inputs
        # Node inputs must be globally provided (task_ir.inputs) or produced by another node
        global_inputs = set(task_ir.inputs or [])
        for node in dag.nodes:
            node_inputs = node.input or []
            if isinstance(node_inputs, str):
                node_inputs = [node_inputs]
            
            for inp in node_inputs:
                if inp not in global_inputs and inp not in all_node_outputs:
                    diagnostics.append(Diagnostic(
                        severity=DiagnosticSeverity.ERROR,
                        pass_name="ValidationPass",
                        node_id=node.node_id,
                        message=f"Node '{node.node_id}' consumes input '{inp}' which is not produced by any node or global input.",
                        suggestion=f"Provide '{inp}' in global task inputs or modify node outputs."
                    ))

        # 4. Check missing outputs
        # Global outputs must be produced by at least one node
        global_outputs = task_ir.outputs or []
        for out in global_outputs:
            if out not in all_node_outputs and out not in global_inputs:
                diagnostics.append(Diagnostic(
                    severity=DiagnosticSeverity.ERROR,
                    pass_name="ValidationPass",
                    message=f"Global output '{out}' is required but not produced by any node in the execution graph.",
                    suggestion="Add a node that produces this output or check symbol names."
                ))

        # 5. Check cycles using NetworkX Graph
        # Build temp graph for checks (only valid nodes)
        valid_nodes = [node for node in dag.nodes if node.node_id]
        valid_node_ids = {n.node_id for n in valid_nodes}
        valid_deps = [dep for dep in dag.dependencies if dep.source in valid_node_ids and dep.target in valid_node_ids]
        
        g = ExecutionGraph(nodes=valid_nodes, dependencies=valid_deps)
        if g.has_cycle():
            cycle_edges = g.find_cycle()
            cycle_str = " -> ".join(f"{u}->{v}" for u, v in cycle_edges)
            diagnostics.append(Diagnostic(
                severity=DiagnosticSeverity.ERROR,
                pass_name="ValidationPass",
                message=f"Dependency cycle detected: {cycle_str}",
                suggestion="Remove cyclic dependency edges in your sequence flow."
            ))

        return state.model_copy(update={"diagnostics": diagnostics})
