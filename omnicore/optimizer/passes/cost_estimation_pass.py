from typing import List, Dict
from omnicore.optimizer.pass_manager import BaseOptimizerPass
from omnicore.optimizer.optimization_context import OptimizerState, Diagnostic, DiagnosticSeverity, OptimizedExecutionDAG, OptimizedExecutionNode
from omnicore.ir.enums import Capability
from omnicore.graph.execution_graph import ExecutionGraph

class CostEstimationPass(BaseOptimizerPass):
    """
    Pass 6: Heuristically estimates execution time, token usage, API cost,
    memory usage, confidence score, and critical path length.
    All calculations are local heuristics and do not call external APIs.
    """
    def run(self, state: OptimizerState) -> OptimizerState:
        diagnostics: List[Diagnostic] = list(state.diagnostics)
        dag = state.execution_dag

        # Heuristic rules per Capability
        TIME_HEURISTICS = {
            Capability.WEB_SEARCH: 8.0,
            Capability.CODE_GENERATION: 12.0,
            Capability.SUMMARIZATION: 4.0,
            Capability.COMPARISON: 5.0,
            Capability.TRANSLATION: 3.0,
            Capability.REASONING: 15.0,
            Capability.RETRIEVAL: 2.0,
            Capability.REPORT_GENERATION: 10.0,
            Capability.EMAIL: 1.5,
            Capability.PDF_GENERATION: 6.0,
            Capability.DATABASE_ACCESS: 2.0,
            Capability.UNKNOWN: 5.0,
        }

        TOKEN_HEURISTICS = {
            Capability.WEB_SEARCH: 600,
            Capability.CODE_GENERATION: 1500,
            Capability.SUMMARIZATION: 1000,
            Capability.COMPARISON: 800,
            Capability.TRANSLATION: 500,
            Capability.REASONING: 2000,
            Capability.RETRIEVAL: 400,
            Capability.REPORT_GENERATION: 3000,
            Capability.EMAIL: 300,
            Capability.PDF_GENERATION: 500,
            Capability.DATABASE_ACCESS: 200,
            Capability.UNKNOWN: 500,
        }

        MEMORY_HEURISTICS = {
            Capability.WEB_SEARCH: 64.0,
            Capability.CODE_GENERATION: 128.0,
            Capability.SUMMARIZATION: 64.0,
            Capability.COMPARISON: 64.0,
            Capability.TRANSLATION: 64.0,
            Capability.REASONING: 256.0,
            Capability.RETRIEVAL: 64.0,
            Capability.REPORT_GENERATION: 128.0,
            Capability.EMAIL: 32.0,
            Capability.PDF_GENERATION: 128.0,
            Capability.DATABASE_ACCESS: 64.0,
            Capability.UNKNOWN: 64.0,
        }

        COST_PER_TOKEN = 0.00002  # $0.02 per 1K tokens
        SEARCH_FLAT_COST = 0.01   # $0.01 per search query

        updated_nodes: List[OptimizedExecutionNode] = []
        total_tokens = 0
        total_cost = 0.0

        # 1. Update individual nodes
        for node in dag.nodes:
            cap = node.capability
            
            # Time & Token estimations
            est_time = TIME_HEURISTICS.get(cap, 5.0)
            est_tokens = TOKEN_HEURISTICS.get(cap, 500)
            est_memory = MEMORY_HEURISTICS.get(cap, 64.0)

            # API Cost calculation
            est_cost = est_tokens * COST_PER_TOKEN
            if cap == Capability.WEB_SEARCH:
                est_cost += SEARCH_FLAT_COST

            total_tokens += est_tokens
            total_cost += est_cost

            # Copy node with computed estimates
            new_node = node.model_copy(update={
                "estimated_time": est_time,
                "estimated_cost": round(est_cost, 4),
                "estimated_tokens": est_tokens,
                "estimated_memory": est_memory
            })
            updated_nodes.append(new_node)

        # 2. Build graph to compute critical path length
        g = ExecutionGraph(nodes=updated_nodes, dependencies=list(dag.dependencies))
        crit_path = g.critical_path()
        
        # Cumulative time of nodes on the critical path is the estimated parallel runtime
        est_runtime = sum(g.get_node(nid).estimated_time for nid in crit_path) if crit_path else 0.0

        diagnostics.append(Diagnostic(
            severity=DiagnosticSeverity.NOTE,
            pass_name="CostEstimationPass",
            message=f"Estimated resources: Runtime={est_runtime:.1f}s (Critical Path), Cost=${total_cost:.4f}, Tokens={total_tokens}."
        ))

        new_dag = OptimizedExecutionDAG(
            nodes=updated_nodes,
            dependencies=dag.dependencies,
            topological_order=dag.topological_order,
            stages=dag.stages,
            critical_path=crit_path,
            estimated_runtime=round(est_runtime, 2),
            estimated_cost=round(total_cost, 4),
            estimated_tokens=total_tokens
        )

        return state.model_copy(update={"execution_dag": new_dag, "diagnostics": diagnostics})
