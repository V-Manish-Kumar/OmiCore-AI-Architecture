from typing import Dict, Optional
from omnicore.optimizer.optimization_context import OptimizedExecutionDAG

class DAGVisualizer:
    """
    Renders optimized compiler Execution DAG steps as Mermaid dependency flowcharts.
    """
    @staticmethod
    def visualize(
        dag: OptimizedExecutionDAG,
        node_statuses: Optional[Dict[str, str]] = None,
        show_tokens: bool = False
    ) -> str:
        """
        Translates Execution DAG nodes and input-to-output links into Mermaid TD graphs.
        Supports coloring nodes dynamically based on execution status and displaying token metrics.
        """
        lines = ["graph TD"]
        nodes_map = {n.node_id: n for n in dag.nodes}
        
        # 1. Add styled nodes with optional token decorations
        for node in dag.nodes:
            label = f"{node.name} ({node.capability.value})"
            if show_tokens:
                tokens = getattr(node, "estimated_tokens", 0) or 500
                label += f"<br/>[{tokens} tokens]"
            
            lines.append(f"  {node.node_id}[\"{label}\"]")
            
        # 2. Add edges using output-to-input variables matching
        added_edges = set()
        for i, src_id in enumerate(dag.topological_order):
            if src_id not in nodes_map:
                continue
            src_node = nodes_map[src_id]
            for j in range(i + 1, len(dag.topological_order)):
                tgt_id = dag.topological_order[j]
                if tgt_id not in nodes_map:
                    continue
                tgt_node = nodes_map[tgt_id]
                
                # Check if target inputs consume source outputs
                src_outputs = src_node.output or []
                if isinstance(src_outputs, str):
                    src_outputs = [src_outputs]
                
                tgt_inputs = tgt_node.input or []
                if isinstance(tgt_inputs, str):
                    tgt_inputs = [tgt_inputs]
                
                shared_vars = set(src_outputs) & set(tgt_inputs)
                if shared_vars:
                    var_name = list(shared_vars)[0]
                    if show_tokens:
                        tokens = (getattr(src_node, "estimated_tokens", 500) // 2) or 250
                        edge_label = f"{var_name} ({tokens} tokens)"
                    else:
                        edge_label = var_name
                        
                    edge = f"{src_id} -->|\"{edge_label}\"| {tgt_id}"
                    if edge not in added_edges:
                        lines.append(f"  {edge}")
                        added_edges.add(edge)
        
        # 3. Add styling based on node execution status
        if node_statuses:
            for node_id, status in node_statuses.items():
                status_lower = status.lower() if status else ""
                if status_lower in ("running", "inprogress"):
                    # Amber highlight
                    lines.append(f"  style {node_id} fill:#fbbf24,stroke:#d97706,stroke-width:2px,color:#1e293b")
                elif status_lower == "completed":
                    # Emerald highlight
                    lines.append(f"  style {node_id} fill:#34d399,stroke:#059669,stroke-width:2px,color:#064e3b")
                elif status_lower == "failed":
                    # Red highlight
                    lines.append(f"  style {node_id} fill:#f87171,stroke:#dc2626,stroke-width:2px,color:#7f1d1d")
                elif status_lower in ("cancelled", "skipped"):
                    # Muted gray highlight
                    lines.append(f"  style {node_id} fill:#94a3b8,stroke:#475569,stroke-width:1px,color:#0f172a")

        return "\n".join(lines)
