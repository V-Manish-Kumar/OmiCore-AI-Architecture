from typing import Dict, Any, List
from omnicore.ir.models import TaskIR
from omnicore.optimizer.optimization_context import OptimizedExecutionDAG

class StateInspector:
    """
    Utility to inspect intermediate compiler structures (AST, IR, Symbol Table)
    and output descriptive debugging metadata.
    """
    @staticmethod
    def inspect_task_ir(task_ir: TaskIR) -> Dict[str, Any]:
        """Inspects TaskIR structure and outputs descriptive metadata."""
        return {
            "task_id": task_ir.task_id,
            "primary_intent": task_ir.primary_intent.value,
            "required_capabilities": [c.value for c in task_ir.required_capabilities],
            "inputs": list(task_ir.inputs),
            "outputs": list(task_ir.outputs),
            "constraints": list(task_ir.constraints),
            "confidence_score": task_ir.confidence_score
        }

    @staticmethod
    def inspect_execution_dag(dag: OptimizedExecutionDAG) -> Dict[str, Any]:
        """Inspects optimized Execution DAG structures."""
        nodes = []
        for node in dag.nodes:
            nodes.append({
                "node_id": node.node_id,
                "name": node.name,
                "capability": node.capability.value,
                "input": node.input,
                "output": node.output
            })
        return {
            "node_count": len(nodes),
            "topological_order": list(dag.topological_order),
            "nodes": nodes
        }
