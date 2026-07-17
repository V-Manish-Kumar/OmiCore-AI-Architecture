from omnicore.optimizer.optimization_context import OptimizedExecutionDAG

class DAGVisualizer:
    """
    Renders optimized compiler Execution DAG steps as Mermaid dependency flowcharts.
    """
    @staticmethod
    def visualize(dag: OptimizedExecutionDAG) -> str:
        """
        Translates Execution DAG nodes and input-to-output links into Mermaid TD graphs.
        """
        lines = ["graph TD"]
        nodes_map = {n.node_id: n for n in dag.nodes}
        
        # 1. Add styled nodes
        for node in dag.nodes:
            lines.append(f"  {node.node_id}[\"{node.name} ({node.capability.value})\"]")
            
        # 2. Add edges using output-to-input variables matching
        added_edges = set()
        for i, src_id in enumerate(dag.topological_order):
            src_node = nodes_map[src_id]
            for j in range(i + 1, len(dag.topological_order)):
                tgt_id = dag.topological_order[j]
                tgt_node = nodes_map[tgt_id]
                
                if tgt_node.input == src_node.output:
                    edge = f"{src_id} -->|{src_node.output}| {tgt_id}"
                    if edge not in added_edges:
                        lines.append(f"  {edge}")
                        added_edges.add(edge)
                        
        return "\n".join(lines)
