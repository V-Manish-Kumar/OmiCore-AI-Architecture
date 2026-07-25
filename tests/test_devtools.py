import pytest
import json
import asyncio
from typing import List
from fastapi.testclient import TestClient
from omnicore.ir.enums import Capability
from omnicore.ir.models import TaskIR
from omnicore.optimizer.optimization_context import OptimizedExecutionNode, OptimizedExecutionDAG
from omnicore.devtools.debugger import CompilerDebugger
from omnicore.devtools.profiler import PerformanceProfiler
from omnicore.devtools.tracer import Tracer
from omnicore.devtools.inspector import StateInspector
from omnicore.visualization.ast_visualizer import ASTVisualizer
from omnicore.visualization.dag_visualizer import DAGVisualizer
from omnicore.dashboard.api import app, wire_devtools
from omnicore.cli.main import build_parser

# --- Test Helpers ---

def create_execution_dag() -> OptimizedExecutionDAG:
    node = OptimizedExecutionNode(
        node_id="search_1",
        name="Search",
        description="Search info",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings"
    )
    return OptimizedExecutionDAG(
        nodes=[node],
        topological_order=["search_1"]
    )

# --- Unit Tests ---

def test_compiler_debugger_breakpoints():
    """Verify debugger triggers registered handler callbacks on breakpoint hits."""
    debugger = CompilerDebugger()
    debugger.set_breakpoint("optimization")
    
    hits = []
    def handler(phase, state):
        hits.append((phase, state))

    debugger.breakpoint_handler = handler

    # 1. Non-breakpoint step
    debugger.step("parsing", {"parsed": True})
    assert len(hits) == 0

    # 2. Breakpoint step
    debugger.step("optimization", {"optimized": True})
    assert len(hits) == 1
    assert hits[0] == ("optimization", {"optimized": True})


def test_performance_profiler():
    """Verify profiler records durations and computes cache hits/misses rate."""
    profiler = PerformanceProfiler()
    profiler.record_phase("parsing", 0.05)
    profiler.record_phase("parsing", 0.07)
    profiler.record_cache_hit()
    profiler.record_cache_hit()
    profiler.record_cache_miss()

    report = profiler.get_performance_report()
    assert report["phase_metrics"]["average_parsing_seconds"] == 0.06
    assert report["caching"]["hits"] == 2
    assert report["caching"]["misses"] == 1
    assert report["caching"]["hit_rate"] == 0.6667


def test_event_tracer_spans():
    """Verify tracer opens/closes spans and exports JSON list formats."""
    tracer = Tracer()
    tracer.start_span("lex_parse", "compilation", {"detail": "start"})
    
    # Wait a bit
    time_sleep = 0.01
    import time
    time.sleep(time_sleep)
    
    tracer.end_span("lex_parse", success=True, metadata={"detail": "complete"})
    
    assert len(tracer.spans) == 1
    span = tracer.spans[0]
    assert span.name == "lex_parse"
    assert span.phase == "compilation"
    assert span.success is True
    assert span.duration_ms > 0
    assert span.metadata["detail"] == "complete"

    exported = tracer.export_traces()
    parsed_json = json.loads(exported)
    assert len(parsed_json) == 1
    assert parsed_json[0]["name"] == "lex_parse"


def test_ast_and_dag_visualizers():
    """Verify visualizers generate correct Mermaid flowchart tree formatting."""
    # 1. AST Visualizer
    class FakeAST:
        def __init__(self):
            self.name = "Root"
            self.goals = []
    class FakeGoal:
        def __init__(self):
            self.name = "Goal1"

    ast = FakeAST()
    ast.goals.append(FakeGoal())
    
    ast_mermaid = ASTVisualizer.visualize(ast)
    assert "graph TD" in ast_mermaid
    assert "Root" in ast_mermaid
    assert "Goal1" in ast_mermaid

    # 2. DAG Visualizer
    dag = create_execution_dag()
    dag_mermaid = DAGVisualizer.visualize(dag)
    assert "graph TD" in dag_mermaid
    assert "search_1" in dag_mermaid

def test_knowledge_graph_visualizer():
    """Verify KnowledgeGraphVisualizer renders Graphify Mermaid and computes token savings."""
    from omnicore.ir.models import TaskIR
    from omnicore.ir.enums import TaskIntent, Capability
    from omnicore.visualization.knowledge_graph_visualizer import KnowledgeGraphVisualizer
    
    task_ir = TaskIR(
        task_id="task_100",
        user_goal="Search web and summarize findings",
        primary_intent=TaskIntent.RESEARCH,
        required_capabilities=[Capability.WEB_SEARCH, Capability.SUMMARIZATION]
    )


    dag = create_execution_dag()
    
    res = KnowledgeGraphVisualizer.visualize(task_ir, dag, original_node_count=3)
    assert "graph TD" in res["mermaid"]
    assert "INTENT" in res["mermaid"]
    assert "SAVINGS" in res["mermaid"]
    assert res["analytics"]["estimated_baseline_tokens"] > 0
    assert res["analytics"]["our_actual_tokens"] > 0
    assert res["analytics"]["tokens_saved"] >= 0
    assert "savings_percentage" in res["analytics"]



def test_cli_args_parsing():
    """Verify devtools CLI parser handles compile, run, status, and debug inputs."""
    parser = build_parser()
    
    # 1. Test compile command
    args_compile = parser.parse_args(["compile", "--query", "summarize report"])
    assert args_compile.command == "compile"
    assert args_compile.query == "summarize report"

    # 2. Test debug command
    args_debug = parser.parse_args(["debug", "--query", "search", "--breakpoints", "parsing,optimization"])
    assert args_debug.command == "debug"
    assert args_debug.breakpoints == "parsing,optimization"


# --- Dashboard API Integration Test ---

def test_fastapi_endpoints():
    """Verify dashboard web console endpoints return valid status payloads."""
    client = TestClient(app)
    
    # Query status endpoint
    status_res = client.get("/api/status")
    assert status_res.status_code == 200
    assert "status" in status_res.json()

    # Query metrics endpoint
    metrics_res = client.get("/api/metrics")
    assert metrics_res.status_code == 200
    assert "completed_tasks" in metrics_res.json()

    # Query traces endpoint
    traces_res = client.get("/api/traces")
    assert traces_res.status_code == 200
    assert isinstance(traces_res.json(), list)

    # Query HTML landing page
    ui_res = client.get("/")
    assert ui_res.status_code == 200
    assert "<html" in ui_res.text
