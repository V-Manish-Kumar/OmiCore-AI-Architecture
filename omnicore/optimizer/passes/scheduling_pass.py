from typing import List, Dict
from omnicore.optimizer.pass_manager import BaseOptimizerPass
from omnicore.optimizer.optimization_context import OptimizerState, Diagnostic, DiagnosticSeverity, OptimizedExecutionDAG, OptimizedExecutionNode
from omnicore.graph.execution_graph import ExecutionGraph
from omnicore.graph.scheduler import TaskScheduler

class SchedulingPass(BaseOptimizerPass):
    """
    Pass 7: Schedules the optimized dependency graph into an Execution DAG.
    Generates:
    - Topological sorting (execution order)
    - Execution stages
    - Parallel groups within stages
    - Critical path
    Updates the final OptimizedExecutionDAG model attributes.
    """
    def run(self, state: OptimizerState) -> OptimizerState:
        diagnostics: List[Diagnostic] = list(state.diagnostics)
        dag = state.execution_dag

        # 1. Build graph and run scheduler
        g = ExecutionGraph(nodes=list(dag.nodes), dependencies=list(dag.dependencies))
        scheduler = TaskScheduler(g)

        topo_order = g.topological_sort()
        stages = scheduler.get_schedule_stages()
        parallel_groups = scheduler.get_parallel_groups()
        crit_path = scheduler.get_critical_path()

        # Update each node's parallel group ID in the node itself
        node_lookup: Dict[str, OptimizedExecutionNode] = {n.node_id: n for n in dag.nodes}
        for group_idx, group in enumerate(parallel_groups):
            if len(group) > 1:
                group_id = f"parallel_group_stage_{group_idx}"
                for nid in group:
                    if nid in node_lookup:
                        node_lookup[nid] = node_lookup[nid].model_copy(update={"parallel_group_id": group_id})

        final_nodes = [node_lookup[n.node_id] for n in dag.nodes]

        # 2. Build and populate the final OptimizedExecutionDAG
        scheduled_dag = OptimizedExecutionDAG(
            nodes=final_nodes,
            dependencies=dag.dependencies,
            topological_order=topo_order,
            stages=stages,
            critical_path=crit_path,
            estimated_runtime=dag.estimated_runtime,
            estimated_cost=dag.estimated_cost,
            estimated_tokens=dag.estimated_tokens
        )

        diagnostics.append(Diagnostic(
            severity=DiagnosticSeverity.NOTE,
            pass_name="SchedulingPass",
            message=f"Scheduled {len(scheduled_dag.nodes)} nodes across {len(stages)} execution stages. Critical path contains {len(crit_path)} nodes."
        ))

        # Save scheduler info to context metadata
        new_metadata = {
            **state.metadata,
            "stages": stages,
            "parallel_groups": parallel_groups,
            "critical_path": crit_path
        }

        return state.model_copy(update={"execution_dag": scheduled_dag, "diagnostics": diagnostics, "metadata": new_metadata})
