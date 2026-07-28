import pytest
from omnicore.parser.intent_parser import IntentParser
from omnicore.optimizer.optimizer import TaskOptimizer
from omnicore.visualization.ast_visualizer import ASTVisualizer
from omnicore.visualization.dag_visualizer import DAGVisualizer
from omnicore.visualization.knowledge_graph_visualizer import KnowledgeGraphVisualizer

def test_end_to_end_graph_generation():
    parser = IntentParser()
    optimizer = TaskOptimizer()

    query = "create a pdf that contains information of ML tools search google for research"
    
    # 1. Compile TaskIR & ExecutionDAG
    task_ir, raw_dag = parser.compile(query)
    ast = parser.ast_parser.parse(query)

    assert task_ir is not None
    assert len(raw_dag.nodes) >= 3

    # 2. Render AST Mermaid
    ast_mermaid = ASTVisualizer.visualize(ast)
    assert "graph TD" in ast_mermaid

    # 3. LLVM Optimizer Pass Execution
    opt_dag, report = optimizer.optimize(task_ir, raw_dag)
    assert opt_dag is not None
    assert len(report.optimization_passes_applied) > 0

    # 4. Render Execution DAG & Optimized DAG
    initial_dag_mermaid = DAGVisualizer.visualize(raw_dag, show_tokens=True)
    optimized_dag_mermaid = DAGVisualizer.visualize(opt_dag, show_tokens=True)
    
    assert "graph TD" in initial_dag_mermaid
    assert "graph TD" in optimized_dag_mermaid

    # 5. Render Graphify Knowledge Graph
    kg_data = KnowledgeGraphVisualizer.visualize(task_ir, opt_dag, original_node_count=len(raw_dag.nodes))
    assert "mermaid" in kg_data
    assert "analytics" in kg_data
    assert "graph TD" in kg_data["mermaid"]
    assert "INTENT" in kg_data["mermaid"]
    assert kg_data["analytics"]["our_actual_tokens"] > 0
