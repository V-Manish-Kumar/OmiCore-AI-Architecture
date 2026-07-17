from typing import List, Dict
from omnicore.optimizer.pass_manager import BaseOptimizerPass
from omnicore.optimizer.optimization_context import OptimizerState, Diagnostic, DiagnosticSeverity, OptimizedExecutionDAG, OptimizedExecutionNode
from omnicore.graph.execution_graph import ExecutionGraph
from omnicore.ir.enums import Capability

class ParallelizationPass(BaseOptimizerPass):
    """
    Pass 4: Analyzes the execution graph to identify independent branches
    and groups nodes that can execute concurrently.
    Sets 'parallelizable' to False for sequential capabilities like PDF, Email, Report.
    Groups nodes within the same scheduling level into parallel groups.
    """
    def run(self, state: OptimizerState) -> OptimizerState:
        diagnostics: List[Diagnostic] = list(state.diagnostics)
        dag = state.execution_dag
        
        # 1. Update node parallelizable flag based on capability
        # PDF generation, report generation, and emailing are sequential/side-effect heavy
        non_parallelizable_caps = {Capability.PDF_GENERATION, Capability.EMAIL, Capability.REPORT_GENERATION}
        
        updated_nodes: List[OptimizedExecutionNode] = []
        node_lookup: Dict[str, OptimizedExecutionNode] = {}
        
        for node in dag.nodes:
            is_parallel = True
            if node.capability in non_parallelizable_caps:
                is_parallel = False
            elif node.parallelizable is False:
                # If already explicitly set to False, keep it False
                is_parallel = False
            
            # Create a copy with the updated parallelizable flag
            new_node = node.model_copy(update={"parallelizable": is_parallel})
            updated_nodes.append(new_node)
            node_lookup[new_node.node_id] = new_node

        # 2. Identify parallel groups by analyzing stages
        g = ExecutionGraph(nodes=updated_nodes, dependencies=list(dag.dependencies))
        stages = g.generate_execution_stages()
        
        parallel_groups: List[List[str]] = []
        for idx, stage in enumerate(stages):
            parallel_candidates = [nid for nid in stage if node_lookup[nid].parallelizable]
            if len(parallel_candidates) > 1:
                # Assign a parallel group ID to these nodes
                group_id = f"parallel_group_stage_{idx}"
                for nid in parallel_candidates:
                    node_lookup[nid] = node_lookup[nid].model_copy(update={"parallel_group_id": group_id})
                parallel_groups.append(parallel_candidates)
                
                diagnostics.append(Diagnostic(
                    severity=DiagnosticSeverity.NOTE,
                    pass_name="ParallelizationPass",
                    message=f"Created parallel group '{group_id}' with nodes: {', '.join(parallel_candidates)}."
                ))

        # Re-assemble final nodes list
        final_nodes = [node_lookup[n.node_id] for n in updated_nodes]
        
        new_dag = OptimizedExecutionDAG(
            nodes=final_nodes,
            dependencies=dag.dependencies,
            topological_order=dag.topological_order,
            stages=dag.stages,
            critical_path=dag.critical_path,
            estimated_runtime=dag.estimated_runtime,
            estimated_cost=dag.estimated_cost,
            estimated_tokens=dag.estimated_tokens
        )
        
        # Save parallel groups list in state metadata
        new_metadata = {**state.metadata, "parallel_groups": parallel_groups}

        return state.model_copy(update={"execution_dag": new_dag, "diagnostics": diagnostics, "metadata": new_metadata})
