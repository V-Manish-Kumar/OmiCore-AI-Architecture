from typing import List
from omnicore.optimizer.pass_manager import BaseOptimizerPass
from omnicore.optimizer.optimization_context import (
    OptimizerState,
    OptimizedExecutionNode,
    OptimizedExecutionDAG,
    CAPABILITY_DESCRIPTOR_MAP,
    UnknownCapability,
    Diagnostic,
    DiagnosticSeverity
)

class CapabilityResolutionPass(BaseOptimizerPass):
    """
    Pass 2: Converts abstract node Capabilities into executable Capability Descriptors.
    Ensures that each node is bound to a compiler capability representation.
    """
    def run(self, state: OptimizerState) -> OptimizerState:
        diagnostics: List[Diagnostic] = list(state.diagnostics)
        dag = state.execution_dag
        
        resolved_nodes: List[OptimizedExecutionNode] = []
        
        for node in dag.nodes:
            # Map Capability enum to concrete Descriptor subclass
            descriptor_cls = CAPABILITY_DESCRIPTOR_MAP.get(node.capability, UnknownCapability)
            
            # Map inputs/outputs to lists for the descriptor
            req_in = node.input if isinstance(node.input, list) else ([node.input] if node.input else [])
            prod_out = node.output if isinstance(node.output, list) else ([node.output] if node.output else [])
            
            descriptor_inst = descriptor_cls(
                required_inputs=req_in,
                produced_outputs=prod_out
            )
            
            # Re-create/copy node as an OptimizedExecutionNode
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
                parallelizable=node.parallelizable,
                resolved_capability=descriptor_inst
            )
            resolved_nodes.append(opt_node)
            
            # Emit optimization note
            diagnostics.append(Diagnostic(
                severity=DiagnosticSeverity.NOTE,
                pass_name="CapabilityResolutionPass",
                node_id=node.node_id,
                message=f"Resolved abstract capability '{node.capability.value}' to descriptor '{descriptor_cls.__name__}'."
            ))

        new_dag = OptimizedExecutionDAG(
            nodes=resolved_nodes,
            dependencies=dag.dependencies,
            topological_order=dag.topological_order,
            stages=dag.stages,
            critical_path=dag.critical_path,
            estimated_runtime=dag.estimated_runtime,
            estimated_cost=dag.estimated_cost,
            estimated_tokens=dag.estimated_tokens
        )

        return state.model_copy(update={"execution_dag": new_dag, "diagnostics": diagnostics})
