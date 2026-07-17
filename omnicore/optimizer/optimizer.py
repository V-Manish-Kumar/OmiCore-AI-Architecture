from typing import Tuple, List
from omnicore.ir.models import TaskIR, ExecutionDAG
from omnicore.optimizer.optimization_context import (
    OptimizerState,
    OptimizedExecutionNode,
    OptimizedExecutionDAG,
    OptimizationReport
)
from omnicore.optimizer.pass_manager import PassManager
from omnicore.optimizer.passes.validation_pass import ValidationPass
from omnicore.optimizer.passes.capability_resolution_pass import CapabilityResolutionPass
from omnicore.optimizer.passes.dependency_analysis_pass import DependencyAnalysisPass
from omnicore.optimizer.passes.parallelization_pass import ParallelizationPass
from omnicore.optimizer.passes.graph_optimization_pass import GraphOptimizationPass
from omnicore.optimizer.passes.cost_estimation_pass import CostEstimationPass
from omnicore.optimizer.passes.scheduling_pass import SchedulingPass
from omnicore.optimizer.passes.optimization_report_pass import OptimizationReportPass

class TaskOptimizer:
    """
    Main entry point orchestrator for the OmniCore Task Optimization Pipeline.
    Initializes a default pass pipeline and lowers TaskIR + ExecutionDAG
    into a scheduling-aware OptimizedExecutionDAG and OptimizationReport.
    """
    def __init__(self):
        self.pass_manager = PassManager()
        self._register_default_pipeline()

    def _register_default_pipeline(self) -> None:
        # 1. Register all passes
        self.pass_manager.register_pass("validation", ValidationPass())
        self.pass_manager.register_pass("capability_resolution", CapabilityResolutionPass())
        self.pass_manager.register_pass("dependency_analysis", DependencyAnalysisPass())
        self.pass_manager.register_pass("parallelization", ParallelizationPass())
        self.pass_manager.register_pass("graph_optimization", GraphOptimizationPass())
        self.pass_manager.register_pass("cost_estimation", CostEstimationPass())
        self.pass_manager.register_pass("scheduling", SchedulingPass())
        self.pass_manager.register_pass("optimization_report", OptimizationReportPass())

        # 2. Configure default pipeline ordering
        self.pass_manager.set_pipeline_order([
            "validation",
            "capability_resolution",
            "dependency_analysis",
            "parallelization",
            "graph_optimization",
            "cost_estimation",
            "scheduling",
            "optimization_report"
        ])

    def optimize(self, task_ir: TaskIR, execution_dag: ExecutionDAG) -> Tuple[OptimizedExecutionDAG, OptimizationReport]:
        """
        Compiles and optimizes the given TaskIR and ExecutionDAG.
        Returns a tuple of (OptimizedExecutionDAG, OptimizationReport).
        Raises ValidationError if validation or cycles fail compiling.
        """
        # Convert incoming nodes to OptimizedExecutionNode instances
        opt_nodes: List[OptimizedExecutionNode] = []
        original_node_ids = []
        
        for node in execution_dag.nodes:
            original_node_ids.append(node.node_id)
            opt_node = OptimizedExecutionNode(
                node_id=node.node_id,
                name=node.name,
                description=node.description,
                capability=node.capability,
                input=node.input,
                output=node.output,
                status=node.status,
                estimated_cost=node.estimated_cost,
                estimated_time=node.estimated_time,
                parallelizable=node.parallelizable
            )
            opt_nodes.append(opt_node)

        # Build initial DAG wrapper
        initial_dag = OptimizedExecutionDAG(
            nodes=opt_nodes,
            dependencies=execution_dag.dependencies,
            topological_order=execution_dag.topological_order
        )

        # Initialize Optimizer State
        state = OptimizerState(
            task_ir=task_ir,
            execution_dag=initial_dag,
            metadata={"original_nodes": original_node_ids}
        )

        # Run pipeline
        final_state = self.pass_manager.run(state)

        # Extract optimized DAG and optimization report
        opt_dag = final_state.execution_dag
        report = final_state.metadata["optimization_report"]

        return opt_dag, report
