import os
from fastapi import FastAPI, responses
from fastapi.staticfiles import StaticFiles
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from omnicore.devtools.tracer import Tracer
from omnicore.devtools.profiler import PerformanceProfiler
from omnicore.distributed.cluster_manager import DistributedClusterManager
from omnicore.parser.intent_parser import IntentParser
from omnicore.optimizer.optimizer import TaskOptimizer
from omnicore.visualization.dag_visualizer import DAGVisualizer
from omnicore.visualization.ast_visualizer import ASTVisualizer
from omnicore.visualization.knowledge_graph_visualizer import KnowledgeGraphVisualizer
from omnicore.runtime.runtime import AdaptiveRuntime

from omnicore.runtime.adapters.capability_adapter import MockCapabilityAdapter
from omnicore.ir.enums import Capability
from omnicore.cluster.resource import ResourceState

app = FastAPI(title="OmniCore AI Compiler IDE", version="2.0.0")


# Mount React dist static assets if built
dist_dir = os.path.join(os.path.dirname(__file__), "dist")
assets_dir = os.path.join(dist_dir, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Shared devtools instances connected to runtime
shared_tracer = Tracer()
shared_profiler = PerformanceProfiler()
shared_cluster: Optional[DistributedClusterManager] = None

class SandboxRequest(BaseModel):
    query: str

class TopologyNode(BaseModel):
    node_id: str
    name: str
    capability: str
    input: str
    output: str

class TopologyRequest(BaseModel):
    nodes: List[TopologyNode]

import asyncio
import uuid

# Active query executions registry
active_executions: Dict[str, Dict[str, Any]] = {}

async def run_pipeline_execution(execution_id: str, query: str):
    exec_state = active_executions[execution_id]
    try:
        parser = IntentParser()
        optimizer = TaskOptimizer()

        # Token calculations based on lexical words count
        raw_tokens = len(query.split())
        optimized_tokens = max(1, int(raw_tokens * 0.75))
        savings_pct = round(((raw_tokens - optimized_tokens) / max(1, raw_tokens)) * 100.0, 1)

        exec_state["logs"].append("> Running Intent Analysis and Syntax Parsing...")
        task_ir, raw_dag = parser.compile(query)
        ast = parser.ast_parser.parse(query)
        ast_mermaid = ASTVisualizer.visualize(ast)

        exec_state["logs"].append("> Running LLVM-Style Optimization passes...")
        opt_dag, report = optimizer.optimize(task_ir, raw_dag)
        
        # Initial and Optimized DAG diagrams
        initial_dag_mermaid = DAGVisualizer.visualize(raw_dag, show_tokens=True)
        optimized_dag_mermaid = DAGVisualizer.visualize(opt_dag, show_tokens=True)

        kg_data = KnowledgeGraphVisualizer.visualize(task_ir, opt_dag, original_node_count=len(raw_dag.nodes))

        exec_state.update({
            "status": "running",
            "ast_mermaid": ast_mermaid,
            "initial_dag_mermaid": initial_dag_mermaid,
            "optimized_dag_mermaid": optimized_dag_mermaid,
            "current_dag_mermaid": optimized_dag_mermaid,
            "graphify_mermaid": kg_data["mermaid"],
            "graphify_analytics": kg_data["analytics"],
            "passes": report.optimization_passes_applied,
            "token_stats": {
                "raw_tokens": kg_data["analytics"]["estimated_baseline_tokens"],
                "optimized_tokens": kg_data["analytics"]["our_actual_tokens"],
                "savings_percentage": kg_data["analytics"]["savings_percentage"]
            },
            "cost_estimation": {
                "runtime": round(report.estimated_runtime, 4),
                "cost": round(report.estimated_cost, 4),
                "tokens": report.estimated_tokens
            },
            "realtime_metrics": {
                "completed_nodes": 0,
                "total_nodes": len(opt_dag.nodes),
                "total_tokens_processed": 0,
                "total_tokens_saved": kg_data["analytics"]["tokens_saved"]
            }
        })
        
        for node in opt_dag.nodes:
            exec_state["node_statuses"][node.node_id] = "Pending"

        exec_state["logs"].append(f"> Compiled {len(opt_dag.nodes)} optimized nodes into Knowledge Graph. Initializing Adaptive Runtime...")

        # Setup runtime with simulated visual latency (e.g. 1.2s per node)
        adapter = MockCapabilityAdapter(latency=1.2)
        runtime = AdaptiveRuntime(adapter=adapter)

        # Event handler to capture node transitions
        def on_event(event):
            evt_type = event.event_type
            data = event.data
            nid = data.get("node_id")

            if evt_type == "node_started":
                exec_state["node_statuses"][nid] = "Running"
                exec_state["logs"].append(f"> Node '{nid}' started execution using capability: {data.get('capability')}")
                if shared_cluster:
                    cap_str = str(data.get('capability'))
                    for w in shared_cluster.registry.workers.values():
                        caps = [c.value if hasattr(c, "value") else str(c) for c in w["capabilities"]]
                        if cap_str in caps or any(cap_str in c for c in caps):
                            w["active_tasks"] = 1
                            w["current_node"] = nid
                            break
            elif evt_type == "node_completed":
                exec_state["node_statuses"][nid] = "Completed"
                exec_state["realtime_metrics"]["completed_nodes"] += 1
                node_tokens = 500  # standard heuristic
                exec_state["realtime_metrics"]["total_tokens_processed"] += node_tokens
                exec_state["logs"].append(f"> Node '{nid}' completed successfully. Outputs: {data.get('outputs')}")
                if shared_cluster:
                    for w in shared_cluster.registry.workers.values():
                        if w.get("current_node") == nid:
                            w["active_tasks"] = 0
                            w["current_node"] = None
            elif evt_type == "node_failed":
                exec_state["node_statuses"][nid] = "Failed"
                exec_state["logs"].append(f"> Node '{nid}' failed execution: {data.get('error')}")
                if shared_cluster:
                    for w in shared_cluster.registry.workers.values():
                        if w.get("current_node") == nid:
                            w["active_tasks"] = 0
                            w["current_node"] = None

            # Re-generate current DAG Mermaid with colored highlights
            exec_state["current_dag_mermaid"] = DAGVisualizer.visualize(
                opt_dag,
                node_statuses=exec_state["node_statuses"],
                show_tokens=True
            )

        runtime.context.event_bus.subscribe("*", on_event)

        exec_state["logs"].append("> Dynamic runtime scheduler started...")
        result = await runtime.execute(opt_dag, inputs={"query": query})

        if shared_cluster:
            for w in shared_cluster.registry.workers.values():
                w["active_tasks"] = 0
                w["current_node"] = None

        exec_state["status"] = "completed" if result.status.value == "Completed" else "failed"
        exec_state["final_outputs"] = result.outputs
        exec_state["logs"].append(f"> Runtime execution finished with status: {result.status.value}")


    except Exception as e:
        exec_state["status"] = "failed"
        exec_state["logs"].append(f"> COMPILE/RUNTIME ERROR: {str(e)}")

@app.post("/api/execute")
async def execute_query(req: SandboxRequest) -> Dict[str, Any]:
    """Compiles the query and runs task execution on a background thread/task."""
    execution_id = f"exec_{uuid.uuid4().hex[:8]}"
    active_executions[execution_id] = {
        "status": "compiling",
        "query": req.query,
        "ast_mermaid": "",
        "initial_dag_mermaid": "",
        "optimized_dag_mermaid": "",
        "current_dag_mermaid": "",
        "graphify_mermaid": "",
        "graphify_analytics": {"estimated_baseline_tokens": 0, "our_actual_tokens": 0, "tokens_saved": 0, "savings_percentage": 0.0},
        "passes": [],
        "node_statuses": {},
        "logs": ["> Compiler pipeline initialized."],
        "token_stats": {"raw_tokens": 0, "optimized_tokens": 0, "savings_percentage": 0.0},
        "cost_estimation": {"runtime": 0.0, "cost": 0.0, "tokens": 0},
        "realtime_metrics": {"completed_nodes": 0, "total_nodes": 0, "total_tokens_processed": 0, "total_tokens_saved": 0},
        "final_outputs": {}
    }
    # Spawn background task
    asyncio.create_task(run_pipeline_execution(execution_id, req.query))
    return {"success": True, "execution_id": execution_id}

@app.get("/api/execution/{execution_id}")
def get_execution_status(execution_id: str) -> Dict[str, Any]:
    """Returns the current execution details, logs, and token stats."""
    if execution_id not in active_executions:
        return {"success": False, "error": "Execution ID not found"}
    return active_executions[execution_id]

def get_or_create_cluster() -> DistributedClusterManager:
    global shared_cluster
    if shared_cluster is None:
        cluster = DistributedClusterManager()
        cluster.register_worker(
            "worker_search_node_01",
            ResourceState(cpu_cores=8, memory_mb=16384, gpu_count=1),
            [Capability.WEB_SEARCH, Capability.RETRIEVAL]
        )
        cluster.register_worker(
            "worker_summarize_node_02",
            ResourceState(cpu_cores=16, memory_mb=32768, gpu_count=2),
            [Capability.SUMMARIZATION, Capability.COMPARISON, Capability.TRANSLATION, Capability.REASONING]
        )
        cluster.register_worker(
            "worker_generator_node_03",
            ResourceState(cpu_cores=8, memory_mb=16384, gpu_count=1),
            [Capability.CODE_GENERATION, Capability.REPORT_GENERATION, Capability.PDF_GENERATION, Capability.EMAIL, Capability.DATABASE_ACCESS]
        )
        shared_cluster = cluster
    return shared_cluster

def wire_devtools(cluster: DistributedClusterManager, tracer: Tracer, profiler: PerformanceProfiler):
    global shared_cluster, shared_tracer, shared_profiler
    shared_cluster = cluster
    shared_tracer = tracer
    shared_profiler = profiler

@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    cluster = get_or_create_cluster()
    return cluster.status()

@app.get("/api/metrics")
def get_metrics() -> Dict[str, Any]:
    cluster = get_or_create_cluster()
    return cluster.metrics()


@app.get("/api/traces")
def get_traces() -> List[Dict[str, Any]]:
    return [span.model_dump() for span in shared_tracer.spans]

@app.get("/api/profiler")
def get_profiler() -> Dict[str, Any]:
    return shared_profiler.get_performance_report()

@app.post("/api/compile_sandbox")
async def compile_sandbox(req: SandboxRequest) -> Dict[str, Any]:
    """Compiles a natural language query, counts tokens, and estimates optimization savings."""
    try:
        parser = IntentParser()
        optimizer = TaskOptimizer()

        task_ir, raw_dag = parser.compile(req.query)
        ast = parser.ast_parser.parse(req.query)
        ast_mermaid = ASTVisualizer.visualize(ast)

        opt_dag, report = optimizer.optimize(task_ir, raw_dag)
        dag_mermaid = DAGVisualizer.visualize(opt_dag)

        kg_data = KnowledgeGraphVisualizer.visualize(task_ir, opt_dag, original_node_count=len(raw_dag.nodes))

        return {
            "success": True,
            "ast_mermaid": ast_mermaid,
            "dag_mermaid": dag_mermaid,
            "graphify_mermaid": kg_data["mermaid"],
            "graphify_analytics": kg_data["analytics"],
            "passes": report.optimization_passes_applied,
            "token_stats": {
                "raw_tokens": kg_data["analytics"]["estimated_baseline_tokens"],
                "optimized_tokens": kg_data["analytics"]["our_actual_tokens"],
                "savings_percentage": kg_data["analytics"]["savings_percentage"]
            },
            "cost_estimation": {
                "runtime": round(report.estimated_runtime, 4),
                "cost": round(report.estimated_cost, 4),
                "tokens": report.estimated_tokens
            },
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "ast_mermaid": "",
            "dag_mermaid": "",
            "graphify_mermaid": "",
            "graphify_analytics": {"estimated_baseline_tokens": 0, "our_actual_tokens": 0, "tokens_saved": 0, "savings_percentage": 0.0},
            "passes": [],
            "token_stats": {"raw_tokens": 0, "optimized_tokens": 0, "savings_percentage": 0.0},
            "cost_estimation": {},
            "error": str(e)
        }


@app.post("/api/compile_topology")
def compile_topology(req: TopologyRequest) -> Dict[str, Any]:
    """Dynamically compiles topology nodes list, detecting cycles and topological sorts."""
    try:
        nodes = req.nodes
        if not nodes:
            return {
                "success": True,
                "topological_order": [],
                "dag_mermaid": "graph TD\n  empty[\"Empty Topology\"]",
                "cost_estimation": {"runtime": 0.0, "cost": 0.0, "tokens": 0},
                "diagnostics": ["Warning: No compilation nodes declared."]
            }

        # 1. Kahn's algorithm for topological sorting and cycle detection
        in_degree = {n.node_id: 0 for n in nodes}
        adj = {n.node_id: [] for n in nodes}
        
        # Build edges where target input variable matches source output variable
        for src in nodes:
            for tgt in nodes:
                if src.node_id != tgt.node_id and tgt.input == src.output:
                    adj[src.node_id].append(tgt.node_id)
                    in_degree[tgt.node_id] += 1

        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        order = []
        while queue:
            u = queue.pop(0)
            order.append(u)
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        if len(order) != len(nodes):
            raise ValueError("Dependency loop / Cycle detected in topology compilation!")

        # 2. Build Mermaid DAG string
        lines = ["graph TD"]
        for n in nodes:
            lines.append(f"  {n.node_id}[\"{n.name} ({n.capability})\"]")
        
        added_edges = set()
        for src in nodes:
            for tgt in nodes:
                if src.node_id != tgt.node_id and tgt.input == src.output:
                    edge = f"{src.node_id} -->|{src.output}| {tgt.node_id}"
                    if edge not in added_edges:
                        lines.append(f"  {edge}")
                        added_edges.add(edge)

        dag_mermaid = "\n".join(lines)

        return {
            "success": True,
            "topological_order": order,
            "dag_mermaid": dag_mermaid,
            "cost_estimation": {
                "runtime": round(len(nodes) * 0.05, 3),
                "cost": round(len(nodes) * 0.0012, 4),
                "tokens": len(nodes) * 90
            },
            "diagnostics": [f"Success: Compiled successfully. Execution order: {' -> '.join(order)}"]
        }
    except Exception as e:
        return {
            "success": False,
            "topological_order": [],
            "dag_mermaid": "",
            "cost_estimation": {},
            "diagnostics": [f"Error: Compilation failed. Details: {str(e)}"]
        }

@app.get("/", response_class=responses.HTMLResponse)
def get_ui():
    """Returns the React Liquid Glass Dashboard SPA."""
    index_file = os.path.join(dist_dir, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return responses.HTMLResponse(content=f.read())
    return responses.HTMLResponse(content="<h1>OmniCore React Dashboard not built yet. Run 'npm run build' inside omnicore/dashboard/frontend.</h1>")
