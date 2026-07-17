from typing import Any

class ASTVisualizer:
    """
    Renders compiler AST tree nodes as Mermaid syntax flowcharts.
    """
    @staticmethod
    def visualize(ast_node: Any) -> str:
        """
        Recursively traverses AST node structure to build a Mermaid flowchart string.
        """
        lines = ["graph TD"]
        visited_ids = set()

        def traverse(node: Any, parent_id: str = None) -> None:
            if node is None or id(node) in visited_ids:
                return
            visited_ids.add(id(node))

            node_id = f"node_{id(node)}"
            
            # Formulate node label
            node_name = getattr(node, "__class__", {}).__name__
            if hasattr(node, "value"):
                node_label = f"{node_name}: {node.value}"
            elif hasattr(node, "name"):
                node_label = f"{node_name}: {node.name}"
            elif hasattr(node, "intent"):
                node_label = f"{node_name}: {node.intent}"
            elif hasattr(node, "user_goal"):
                node_label = f"{node_name}: {node.user_goal[:20]}"
            else:
                node_label = node_name

            lines.append(f"  {node_id}[\"{node_label}\"]")

            if parent_id:
                lines.append(f"  {parent_id} --> {node_id}")

            # Recurse children attributes
            if hasattr(node, "goals"):
                # Module 1 AST goals list
                goals = getattr(node, "goals", [])
                if isinstance(goals, list):
                    for g in goals:
                        traverse(g, node_id)
            elif hasattr(node, "__dict__"):
                for k, v in node.__dict__.items():
                    if hasattr(v, "__dict__"):
                        traverse(v, node_id)
                    elif isinstance(v, list):
                        for item in v:
                            if hasattr(item, "__dict__"):
                                traverse(item, node_id)

        traverse(ast_node)
        return "\n".join(lines)
