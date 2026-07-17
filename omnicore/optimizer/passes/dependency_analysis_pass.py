from typing import List, Dict, Set, Tuple
from omnicore.optimizer.pass_manager import BaseOptimizerPass
from omnicore.optimizer.optimization_context import OptimizerState, Diagnostic, DiagnosticSeverity, OptimizedExecutionDAG
from omnicore.ir.models import Dependency
from omnicore.graph.execution_graph import ExecutionGraph

class DependencyAnalysisPass(BaseOptimizerPass):
    """
    Pass 3: Constructs and analyzes node dependency relationships.
    Specifically:
    - Infers data dependencies where node B consumes outputs produced by node A.
    - Preserves control dependencies defined in the compilation input.
    - Labels each dependency and constructs a clean dependency graph.
    """
    def run(self, state: OptimizerState) -> OptimizerState:
        diagnostics: List[Diagnostic] = list(state.diagnostics)
        dag = state.execution_dag
        
        # Build node output-to-producer map
        producer_map: Dict[str, str] = {}  # symbol_name -> node_id
        for node in dag.nodes:
            outputs = node.output or []
            if isinstance(outputs, str):
                outputs = [outputs]
            for out in outputs:
                producer_map[out] = node.node_id

        # 1. Reconstruct all dependencies
        inferred_deps: Set[Tuple[str, str]] = set()
        
        # Find data dependencies: nodes consuming outputs from other nodes
        for node in dag.nodes:
            inputs = node.input or []
            if isinstance(inputs, str):
                inputs = [inputs]
            for inp in inputs:
                if inp in producer_map:
                    producer = producer_map[inp]
                    if producer != node.node_id:
                        inferred_deps.add((producer, node.node_id))

        # Preserve existing control dependencies
        # Any existing dependency in DAG is considered a control dependency unless it is also a data dependency
        all_deps_keys: Set[Tuple[str, str]] = set()
        for dep in dag.dependencies:
            all_deps_keys.add((dep.source, dep.target))

        # Union of inferred and existing dependencies
        combined_dep_keys = inferred_deps.union(all_deps_keys)

        # Convert back to Dependency objects
        final_dependencies: List[Dependency] = [
            Dependency(source=u, target=v) for u, v in sorted(combined_dep_keys)
        ]

        # 2. Check for cycles introduced by dependency expansion
        g = ExecutionGraph(nodes=list(dag.nodes), dependencies=final_dependencies)
        if g.has_cycle():
            cycle_edges = g.find_cycle()
            cycle_str = " -> ".join(f"{u}->{v}" for u, v in cycle_edges)
            diagnostics.append(Diagnostic(
                severity=DiagnosticSeverity.ERROR,
                pass_name="DependencyAnalysisPass",
                message=f"Cycle detected after dependency construction: {cycle_str}",
                suggestion="Check for circular dataflow/outputs in nodes."
            ))
        else:
            diagnostics.append(Diagnostic(
                severity=DiagnosticSeverity.NOTE,
                pass_name="DependencyAnalysisPass",
                message=f"Constructed dependency graph with {len(final_dependencies)} edges ({len(inferred_deps)} data-driven)."
            ))

        new_dag = OptimizedExecutionDAG(
            nodes=dag.nodes,
            dependencies=final_dependencies,
            topological_order=dag.topological_order,
            stages=dag.stages,
            critical_path=dag.critical_path,
            estimated_runtime=dag.estimated_runtime,
            estimated_cost=dag.estimated_cost,
            estimated_tokens=dag.estimated_tokens
        )

        return state.model_copy(update={"execution_dag": new_dag, "diagnostics": diagnostics})
