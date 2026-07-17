from typing import List, Dict, Set, Tuple
from omnicore.optimizer.pass_manager import BaseOptimizerPass
from omnicore.optimizer.optimization_context import OptimizerState, Diagnostic, DiagnosticSeverity, OptimizedExecutionDAG, OptimizedExecutionNode
from omnicore.ir.models import Dependency
from omnicore.ir.enums import Capability

class GraphOptimizationPass(BaseOptimizerPass):
    """
    Pass 5: Optimizes the execution graph by running:
    - Duplicate Node Elimination (Common Capability / Common Subexpression Elimination):
      Merges non-side-effect nodes with identical capabilities and inputs.
      Redirects dependencies and renames/maps output symbols.
    - Dead Node Elimination:
      Removes nodes that don't produce any needed outputs (not in global outputs and not consumed by other nodes)
      and don't have side effects, run iteratively until convergence.
    - Constant Metadata Propagation:
      Aggregates constraints and propagates metadata.
    """
    def run(self, state: OptimizerState) -> OptimizerState:
        diagnostics: List[Diagnostic] = list(state.diagnostics)
        dag = state.execution_dag
        task_ir = state.task_ir

        # Keep track of optimization operations for reporting
        removed_nodes: Set[str] = set()
        merged_nodes: Dict[str, str] = {}  # source -> target

        # Capabilities with side effects (must never be eliminated as dead or merged as duplicates)
        side_effect_caps = {
            Capability.EMAIL,
            Capability.PDF_GENERATION,
            Capability.DATABASE_ACCESS,
            Capability.REPORT_GENERATION
        }

        # Initialize lists of current nodes and dependencies
        nodes_list: List[OptimizedExecutionNode] = [node.model_copy() for node in dag.nodes]
        dependencies_list: List[Dependency] = [dep.model_copy() for dep in dag.dependencies]

        # --- OPTIMIZATION 1: Duplicate Node Elimination ---
        symbol_rename_map: Dict[str, str] = {}
        merged_any = True
        
        while merged_any:
            merged_any = False
            # Find duplicate candidates
            # We group by (capability, tuple of inputs)
            seen_operations: Dict[Tuple[Capability, Tuple[str, ...]], OptimizedExecutionNode] = {}
            node_to_remove = None
            node_to_keep = None

            for node in nodes_list:
                if node.capability in side_effect_caps:
                    continue
                
                # Normalize inputs to a hashable tuple
                node_inputs = node.input or []
                if isinstance(node_inputs, str):
                    node_inputs = [node_inputs]
                # If inputs contain renamed symbols, apply rename map
                resolved_inputs = tuple(symbol_rename_map.get(inp, inp) for inp in node_inputs)

                key = (node.capability, resolved_inputs)
                if key in seen_operations:
                    node_to_keep = seen_operations[key]
                    node_to_remove = node
                    merged_any = True
                    break
                else:
                    seen_operations[key] = node

            if merged_any and node_to_remove and node_to_keep:
                # Merge node_to_remove into node_to_keep
                keep_id = node_to_keep.node_id
                rem_id = node_to_remove.node_id
                
                # Map outputs of node_to_remove to outputs of node_to_keep
                rem_outputs = node_to_remove.output or []
                if isinstance(rem_outputs, str):
                    rem_outputs = [rem_outputs]
                keep_outputs = node_to_keep.output or []
                if isinstance(keep_outputs, str):
                    keep_outputs = [keep_outputs]
                
                # Map by index
                for i in range(min(len(rem_outputs), len(keep_outputs))):
                    symbol_rename_map[rem_outputs[i]] = keep_outputs[i]

                # Update nodes_list: remove the duplicate node
                nodes_list = [n for n in nodes_list if n.node_id != rem_id]
                removed_nodes.add(rem_id)
                merged_nodes[rem_id] = keep_id

                # Update dependencies: redirect all rem_id edges to keep_id
                new_deps: Set[Tuple[str, str]] = set()
                for dep in dependencies_list:
                    src = keep_id if dep.source == rem_id else dep.source
                    tgt = keep_id if dep.target == rem_id else dep.target
                    if src != tgt:  # Avoid self-loops
                        new_deps.add((src, tgt))
                dependencies_list = [Dependency(source=u, target=v) for u, v in sorted(new_deps)]

                diagnostics.append(Diagnostic(
                    severity=DiagnosticSeverity.SUGGESTION,
                    pass_name="GraphOptimizationPass",
                    node_id=rem_id,
                    message=f"Merged duplicate node '{rem_id}' into '{keep_id}' based on identical capability and inputs.",
                    suggestion=f"Reuse the outputs of '{keep_id}'."
                ))

        # Apply final symbol renames to all remaining nodes' inputs
        for node in nodes_list:
            node_inputs = node.input or []
            if isinstance(node_inputs, str):
                node_inputs = [node_inputs]
            
            updated_inputs = [symbol_rename_map.get(inp, inp) for inp in node_inputs]
            node.input = updated_inputs

        # --- OPTIMIZATION 2: Dead Node Elimination ---
        # Run iteratively until no more nodes are removed
        dead_eliminated = True
        global_outputs = set(task_ir.outputs or [])

        while dead_eliminated:
            dead_eliminated = False
            
            # Find all inputs consumed by any current node
            consumed_symbols: Set[str] = set()
            for node in nodes_list:
                node_inputs = node.input or []
                if isinstance(node_inputs, str):
                    node_inputs = [node_inputs]
                for inp in node_inputs:
                    consumed_symbols.add(inp)

            dead_node_id = None
            for node in nodes_list:
                # Do not eliminate side-effect nodes
                if node.capability in side_effect_caps:
                    continue

                # Check if any of its outputs are consumed or globally required
                node_outputs = node.output or []
                if isinstance(node_outputs, str):
                    node_outputs = [node_outputs]
                
                is_needed = False
                for out in node_outputs:
                    # If consumed by another node or is a global output
                    if out in consumed_symbols or out in global_outputs:
                        is_needed = True
                        break
                
                if not is_needed:
                    dead_node_id = node.node_id
                    dead_eliminated = True
                    break

            if dead_eliminated and dead_node_id:
                # Remove this dead node
                nodes_list = [n for n in nodes_list if n.node_id != dead_node_id]
                removed_nodes.add(dead_node_id)
                # Remove its dependencies
                dependencies_list = [d for d in dependencies_list if d.source != dead_node_id and d.target != dead_node_id]
                
                diagnostics.append(Diagnostic(
                    severity=DiagnosticSeverity.SUGGESTION,
                    pass_name="GraphOptimizationPass",
                    node_id=dead_node_id,
                    message=f"Removed dead/unreachable node '{dead_node_id}' because its outputs are never consumed.",
                    suggestion="Verify if this operation was necessary."
                ))

        # --- OPTIMIZATION 3: Constant Metadata Propagation ---
        # Propagate global metadata and constraints into node descriptors or context
        for node in nodes_list:
            if node.resolved_capability:
                # Example of constant propagation: propagate matching global constraints to node metadata
                matching_constraints = [c for c in task_ir.constraints if any(term in c.lower() for term in node.name.lower().split())]
                if matching_constraints:
                    node.description = f"{node.description} [Constraints: {', '.join(matching_constraints)}]"

        # Recompute topological order
        # Build temp graph for topological order
        from omnicore.graph.execution_graph import ExecutionGraph
        g = ExecutionGraph(nodes=nodes_list, dependencies=dependencies_list)
        topo_order = g.topological_sort()

        new_dag = OptimizedExecutionDAG(
            nodes=nodes_list,
            dependencies=dependencies_list,
            topological_order=topo_order,
            stages=dag.stages,
            critical_path=dag.critical_path,
            estimated_runtime=dag.estimated_runtime,
            estimated_cost=dag.estimated_cost,
            estimated_tokens=dag.estimated_tokens
        )

        # Update metadata report fields
        opt_metadata = {
            **state.metadata,
            "removed_nodes": list(removed_nodes),
            "merged_nodes": merged_nodes
        }

        return state.model_copy(update={"execution_dag": new_dag, "diagnostics": diagnostics, "metadata": opt_metadata})
