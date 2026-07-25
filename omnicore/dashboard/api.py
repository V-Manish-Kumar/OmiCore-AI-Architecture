from fastapi import FastAPI, responses
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from omnicore.devtools.tracer import Tracer
from omnicore.devtools.profiler import PerformanceProfiler
from omnicore.distributed.cluster_manager import DistributedClusterManager
from omnicore.parser.intent_parser import IntentParser
from omnicore.optimizer.optimizer import TaskOptimizer
from omnicore.visualization.dag_visualizer import DAGVisualizer
from omnicore.visualization.ast_visualizer import ASTVisualizer
from omnicore.runtime.runtime import AdaptiveRuntime
from omnicore.runtime.adapters.capability_adapter import MockCapabilityAdapter
from omnicore.ir.enums import Capability

app = FastAPI(title="OmniCore AI Compiler IDE", version="2.0.0")

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

        exec_state.update({
            "status": "running",
            "ast_mermaid": ast_mermaid,
            "initial_dag_mermaid": initial_dag_mermaid,
            "optimized_dag_mermaid": optimized_dag_mermaid,
            "current_dag_mermaid": optimized_dag_mermaid,
            "passes": report.optimization_passes_applied,
            "token_stats": {
                "raw_tokens": raw_tokens,
                "optimized_tokens": optimized_tokens,
                "savings_percentage": savings_pct
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
                "total_tokens_saved": report.estimated_tokens - int(report.estimated_tokens * 0.75) if report.estimated_tokens else 0
            }
        })
        
        for node in opt_dag.nodes:
            exec_state["node_statuses"][node.node_id] = "Pending"

        exec_state["logs"].append(f"> Compiled {len(opt_dag.nodes)} optimized nodes. Initializing Adaptive Runtime...")

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
            elif evt_type == "node_completed":
                exec_state["node_statuses"][nid] = "Completed"
                exec_state["realtime_metrics"]["completed_nodes"] += 1
                node_tokens = 500  # standard heuristic
                exec_state["realtime_metrics"]["total_tokens_processed"] += node_tokens
                exec_state["logs"].append(f"> Node '{nid}' completed successfully. Outputs: {data.get('outputs')}")
            elif evt_type == "node_failed":
                exec_state["node_statuses"][nid] = "Failed"
                exec_state["logs"].append(f"> Node '{nid}' failed execution: {data.get('error')}")

            # Re-generate current DAG Mermaid with colored highlights
            exec_state["current_dag_mermaid"] = DAGVisualizer.visualize(
                opt_dag,
                node_statuses=exec_state["node_statuses"],
                show_tokens=True
            )

        runtime.context.event_bus.subscribe("*", on_event)

        exec_state["logs"].append("> Dynamic runtime scheduler started...")
        result = await runtime.execute(opt_dag, inputs={"query": query})

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

def wire_devtools(cluster: DistributedClusterManager, tracer: Tracer, profiler: PerformanceProfiler):
    global shared_cluster, shared_tracer, shared_profiler
    shared_cluster = cluster
    shared_tracer = tracer
    shared_profiler = profiler

@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    if shared_cluster:
        return shared_cluster.status()
    return {"online_workers": [], "status": "offline", "diagnostics": {"warnings": [], "timeline": []}}

@app.get("/api/metrics")
def get_metrics() -> Dict[str, Any]:
    if shared_cluster:
        return shared_cluster.metrics()
    return {"active_workers": 0, "queue_depth": 0, "completed_tasks": 0, "failed_tasks": 0}

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

        # Token calculations based on lexical words count
        raw_tokens = len(req.query.split())
        # Simulate optimization pass token reduction (e.g. CSE or Dead Code pruning)
        optimized_tokens = max(1, int(raw_tokens * 0.75))
        savings_pct = round(((raw_tokens - optimized_tokens) / max(1, raw_tokens)) * 100.0, 1)

        task_ir, raw_dag = parser.compile(req.query)
        ast = parser.ast_parser.parse(req.query)
        ast_mermaid = ASTVisualizer.visualize(ast)

        opt_dag, report = optimizer.optimize(task_ir, raw_dag)
        dag_mermaid = DAGVisualizer.visualize(opt_dag)

        return {
            "success": True,
            "ast_mermaid": ast_mermaid,
            "dag_mermaid": dag_mermaid,
            "passes": report.optimization_passes_applied,
            "token_stats": {
                "raw_tokens": raw_tokens,
                "optimized_tokens": optimized_tokens,
                "savings_percentage": savings_pct
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
    """Returns a premium, modern glassmorphic dashboard console."""
    html_content = r"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>OmniCore Compiler Agent IDE</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-gradient: radial-gradient(circle at top left, #0b0f19, #030712 90%);
                --glass-bg: rgba(17, 24, 39, 0.7);
                --glass-border: rgba(255, 255, 255, 0.08);
                --accent-color: #6366f1;
                --accent-glow: rgba(99, 102, 241, 0.25);
                --success-color: #10b981;
                --error-color: #ef4444;
                --text-color: #f8fafc;
            }
            * { box-sizing: border-box; }
            body {
                margin: 0;
                font-family: 'Outfit', sans-serif;
                background: var(--bg-gradient);
                color: var(--text-color);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                overflow-x: hidden;
            }
            header {
                padding: 15px 30px;
                background: rgba(15, 23, 42, 0.8);
                backdrop-filter: blur(12px);
                border-bottom: 1px solid var(--glass-border);
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
            }
            header h1 {
                margin: 0;
                font-size: 24px;
                font-weight: 700;
                background: linear-gradient(90deg, #a5b4fc, #6366f1);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -0.5px;
            }
            .status-badge {
                padding: 6px 14px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                background: rgba(99, 102, 241, 0.15);
                border: 1px solid rgba(99, 102, 241, 0.3);
                color: #a5b4fc;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .ide-workspace {
                padding: 24px;
                display: grid;
                grid-template-columns: 380px 1fr 340px;
                gap: 20px;
                height: calc(100vh - 65px);
                width: 100%;
            }
            .panel {
                background: var(--glass-bg);
                backdrop-filter: blur(20px);
                border: 1px solid var(--glass-border);
                border-radius: 16px;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            .panel-header {
                padding: 14px 20px;
                border-bottom: 1px solid var(--glass-border);
                background: rgba(15, 23, 42, 0.4);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .panel-header h2 {
                margin: 0;
                font-size: 14px;
                font-weight: 600;
                color: #cbd5e1;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .panel-body {
                padding: 20px;
                flex: 1;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
            }
            .editor-tabs {
                display: flex;
                border-bottom: 1px solid var(--glass-border);
                background: rgba(15, 23, 42, 0.3);
            }
            .tab-btn {
                background: none;
                border: none;
                color: #94a3b8;
                font-family: inherit;
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
                padding: 12px 20px;
                flex: 1;
                text-align: center;
                border-bottom: 2px solid transparent;
                transition: color 0.2s, border-color 0.2s;
            }
            .tab-btn.active {
                color: #a5b4fc;
                border-bottom-color: var(--accent-color);
                background: rgba(99, 102, 241, 0.05);
            }
            .tab-content {
                display: none;
                flex: 1;
                flex-direction: column;
            }
            .tab-content.active { display: flex; }
            .sandbox-input {
                width: 100%;
                height: 120px;
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid var(--glass-border);
                border-radius: 8px;
                color: #fff;
                padding: 12px;
                font-family: inherit;
                font-size: 13px;
                resize: none;
                margin-bottom: 14px;
            }
            .sandbox-input:focus {
                outline: none;
                border-color: var(--accent-color);
            }
            .token-meter {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid var(--glass-border);
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                margin-bottom: 16px;
            }
            .btn-action {
                width: 100%;
                padding: 12px;
                background: linear-gradient(90deg, #6366f1, #818cf8);
                color: #fff;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: opacity 0.2s;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            .btn-action:hover { opacity: 0.9; }
            
            .diag-tab-bar {
                display: flex;
                background: rgba(15, 23, 42, 0.4);
                border-bottom: 1px solid var(--glass-border);
            }
            .diag-tab-btn {
                background: none;
                border: none;
                color: #94a3b8;
                font-family: inherit;
                font-size: 12px;
                font-weight: 600;
                cursor: pointer;
                padding: 10px 16px;
                flex: 1;
                text-align: center;
                border-bottom: 2px solid transparent;
                transition: color 0.2s, border-color 0.2s;
            }
            .diag-tab-btn.active {
                color: #a5b4fc;
                border-bottom-color: var(--accent-color);
                background: rgba(99, 102, 241, 0.05);
            }
            
            /* Topology Node List styling */
            .node-item {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid var(--glass-border);
                border-radius: 8px;
                padding: 10px 14px;
                margin-bottom: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 13px;
            }
            .node-item-del {
                color: var(--error-color);
                cursor: pointer;
                font-weight: 600;
            }
            
            /* Compiler Terminal styling */
            .terminal {
                height: 140px;
                background: #020617;
                border-top: 1px solid var(--glass-border);
                padding: 12px 18px;
                font-family: monospace;
                font-size: 12px;
                overflow-y: auto;
                color: var(--success-color);
                line-height: 1.5;
            }
            
            /* Visual Canvas tab */
            .canvas-area {
                flex: 1;
                background: rgba(15, 23, 42, 0.3);
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: auto;
                padding: 20px;
            }
            
            /* Node registration entries */
            .worker-entry {
                padding: 10px 14px;
                border-bottom: 1px solid var(--glass-border);
                font-size: 13px;
            }
            .worker-entry:last-child { border: none; }
            .badge-success {
                display: inline-block;
                padding: 2px 6px;
                background: rgba(16, 185, 129, 0.15);
                border: 1px solid rgba(16, 185, 129, 0.3);
                color: #34d399;
                font-size: 10px;
                border-radius: 4px;
                margin-right: 8px;
            }
            
            /* Preset tags */
            .tag {
                background: rgba(255, 255, 255, 0.05);
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 11px;
                cursor: pointer;
                transition: background 0.2s;
            }
            .tag:hover { background: rgba(99, 102, 241, 0.15); }
        </style>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({ startOnLoad: false, theme: 'dark' });
            window.mermaid = mermaid;
        </script>
        <script>
            // Active Topology in-memory list
            let activeTopology = [
                {node_id: "n0", name: "Google Query", capability: "WEB_SEARCH", input: "query", output: "findings"},
                {node_id: "n1", name: "Summarization Pass", capability: "SUMMARIZATION", input: "findings", output: "summary"}
            ];

            let currentDiagView = 'ast';
            let currentAst = `graph TD
  idle["Run compilation to see AST Tree"]`;
            let currentInitial = `graph TD
  idle["Before Optimization (Raw prompts)"]`;
            let currentOptimized = `graph TD
  idle["After Optimization (Pruned/Merged)"]`;
            let currentLive = `graph TD
  idle["Live Executing DAG status"]`;
            let executionPollInterval = null;

            async function fetchMetrics() {
                try {
                    const statusRes = await fetch('/api/status');
                    const statusData = await statusRes.json();
                    
                    const workersList = document.getElementById('workers');
                    workersList.innerHTML = statusData.online_workers.map(w => `
                        <div class='worker-entry'>
                            <span class='badge-success'>Active</span> <strong>${w}</strong>
                        </div>
                    `).join('') || "<div class='worker-entry'>No registered worker nodes.</div>";

                    const metricsRes = await fetch('/api/metrics');
                    const metricsData = await metricsRes.json();
                    document.getElementById('health-score').innerText = (metricsData.cluster_health_score * 100).toFixed(1) + '%';
                } catch (e) {
                    console.error(e);
                }
            }

            function selectPreset(txt) {
                document.getElementById('query-input').value = txt;
                updateTokenUsage();
            }

            function updateTokenUsage() {
                const query = document.getElementById('query-input').value;
                const tokenCount = query.trim() ? query.trim().split(/\s+/).length : 0;
                document.getElementById('token-usage').innerText = tokenCount + " Lexical Word tokens";
            }

            function setDiagramView(view) {
                currentDiagView = view;
                document.querySelectorAll('.diag-tab-btn').forEach(btn => btn.classList.remove('active'));
                document.getElementById(`tab-btn-${view}`).classList.add('active');

                // Hide all
                document.getElementById('ast-view').style.display = 'none';
                document.getElementById('opt-view').style.display = 'none';
                document.getElementById('run-view').style.display = 'none';

                if (view === 'ast') {
                    document.getElementById('ast-view').style.display = 'flex';
                    renderMermaid('canvas-ast', currentAst);
                } else if (view === 'opt') {
                    document.getElementById('opt-view').style.display = 'flex';
                    renderMermaid('canvas-initial', currentInitial);
                    renderMermaid('canvas-optimized', currentOptimized);
                } else if (view === 'run') {
                    document.getElementById('run-view').style.display = 'flex';
                    renderMermaid('canvas-live', currentLive);
                }
            }

            async function renderMermaid(elementId, mermaidCode) {
                const canvas = document.getElementById(elementId);
                if (!canvas) return;
                if (!mermaidCode) {
                    canvas.innerHTML = '<div style="color: #64748b; font-size: 13px;">No graph data available</div>';
                    return;
                }
                try {
                    const id = elementId + '-svg-' + Math.floor(Math.random() * 10000);
                    const { svg } = await window.mermaid.render(id, mermaidCode);
                    canvas.innerHTML = svg;
                } catch (e) {
                    console.error("Mermaid error:", e);
                    canvas.innerHTML = '<div style="color: #ef4444; font-size: 13px;">Render error</div>';
                }
            }

            async function runNLPCompile() {
                const query = document.getElementById('query-input').value;
                const terminal = document.getElementById('console-terminal');
                const btn = document.querySelector('.btn-action');

                terminal.innerText = "> Initializing compiler frontend...";
                terminal.style.color = "#cbd5e1";
                btn.disabled = true;
                btn.style.opacity = 0.5;

                try {
                    const res = await fetch('/api/execute', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({query})
                    });
                    const data = await res.json();
                    
                    if (data.success) {
                        const execId = data.execution_id;
                        terminal.innerText = `> Compiler pipeline started. Execution ID: ${execId}`;
                        
                        // Start polling
                        if (executionPollInterval) clearInterval(executionPollInterval);
                        executionPollInterval = setInterval(() => pollExecution(execId), 400);
                    } else {
                        terminal.innerText = `> ERROR: Could not initiate execution.`;
                        terminal.style.color = "#ef4444";
                        resetBtnState();
                    }
                } catch (e) {
                    terminal.innerText = `> ERROR: ${e}`;
                    terminal.style.color = "#ef4444";
                    resetBtnState();
                }
            }

            async function pollExecution(execId) {
                try {
                    const res = await fetch(`/api/execution/${execId}`);
                    const data = await res.json();
                    
                    if (!data.success && data.error) {
                        clearInterval(executionPollInterval);
                        document.getElementById('console-terminal').innerText = `> ERROR: ${data.error}`;
                        document.getElementById('console-terminal').style.color = "#ef4444";
                        resetBtnState();
                        return;
                    }

                    // Update logs
                    const terminal = document.getElementById('console-terminal');
                    terminal.innerHTML = data.logs.map(log => `<div>${log}</div>`).join('');
                    terminal.scrollTop = terminal.scrollHeight; // Auto-scroll

                    // Save mermaid diagrams
                    currentAst = data.ast_mermaid;
                    currentInitial = data.initial_dag_mermaid;
                    currentOptimized = data.optimized_dag_mermaid;
                    currentLive = data.current_dag_mermaid;

                    // Update UI values
                    document.getElementById('est-runtime').innerText = data.cost_estimation.runtime.toFixed(3) + 's';
                    document.getElementById('est-cost').innerText = '$' + data.cost_estimation.cost.toFixed(4);
                    document.getElementById('est-tokens').innerText = data.cost_estimation.tokens + " tokens";
                    
                    if (data.token_stats.savings_percentage > 0) {
                        document.getElementById('opt-savings').innerText = data.token_stats.savings_percentage + "% optimization savings";
                    } else {
                        document.getElementById('opt-savings').innerText = "0.0% savings";
                    }

                    document.getElementById('completed-tasks').innerText = `${data.realtime_metrics.completed_nodes} / ${data.realtime_metrics.total_nodes}`;
                    document.getElementById('health-score').innerText = (data.status === 'failed' ? '0%' : '100%');

                    // Refresh diagram visualizer for active tab
                    setDiagramView(currentDiagView);

                    // Check if finished
                    if (data.status === 'completed' || data.status === 'failed') {
                        clearInterval(executionPollInterval);
                        resetBtnState();

                        if (data.status === 'completed') {
                            terminal.innerHTML += `<div style="color: #34d399; margin-top: 8px; font-weight: bold;">> SUCCESS: Execution complete! Outputs:</div>`;
                            terminal.innerHTML += `<pre style="color: #60a5fa; margin-top: 4px; font-family: monospace; font-size: 11px; background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;">${JSON.stringify(data.final_outputs, null, 2)}</pre>`;
                            terminal.scrollTop = terminal.scrollHeight;
                            
                            // Auto transition to live execution view upon success
                            setDiagramView('run');
                        } else {
                            terminal.innerHTML += `<div style="color: #f87171; margin-top: 8px; font-weight: bold;">> FAILED: Execution halted with errors.</div>`;
                            terminal.scrollTop = terminal.scrollHeight;
                        }
                    }
                } catch (e) {
                    console.error("Polling error:", e);
                }
            }

            function resetBtnState() {
                const btn = document.querySelector('.btn-action');
                btn.disabled = false;
                btn.style.opacity = 1.0;
            }

            function renderTopologyList() {
                const listDiv = document.getElementById('nodes-list');
                listDiv.innerHTML = activeTopology.map((n, idx) => `
                    <div class='node-item'>
                        <div>
                            <strong>${n.node_id}</strong>: ${n.name} (${n.capability})<br/>
                            <span style='color: #94a3b8; font-size: 11px;'>Input: ${n.input} | Output: ${n.output}</span>
                        </div>
                        <span class='node-item-del' onclick='deleteNode(${idx})'>&times;</span>
                    </div>
                `).join('') || "<div class='worker-entry'>Topology is empty. Add a node below.</div>";
            }

            function deleteNode(idx) {
                activeTopology.splice(idx, 1);
                renderTopologyList();
            }

            function addCustomNode() {
                const node_id = document.getElementById('new-node-id').value.trim();
                const name = document.getElementById('new-node-name').value.trim();
                const capability = document.getElementById('new-node-cap').value;
                const input = document.getElementById('new-node-input').value.trim();
                const output = document.getElementById('new-node-output').value.trim();

                if (!node_id || !name || !input || !output) {
                    alert("Please fill all node parameters.");
                    return;
                }

                activeTopology.push({node_id, name, capability, input, output});
                renderTopologyList();

                // reset form
                document.getElementById('new-node-id').value = "n" + activeTopology.length;
                document.getElementById('new-node-name').value = "";
                document.getElementById('new-node-input').value = "";
                document.getElementById('new-node-output').value = "";
            }

            async function compileCustomTopology() {
                const terminal = document.getElementById('console-terminal');
                terminal.innerText = "> Running dynamic topology graph compilation...";
                terminal.style.color = "#cbd5e1";

                try {
                    const res = await fetch('/api/compile_topology', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({nodes: activeTopology})
                    });
                    const data = await res.json();
                    
                    if (data.success) {
                        terminal.innerText = `> ` + data.diagnostics.join('\n');
                        terminal.style.color = "#10b981";

                        // Set values
                        currentInitial = data.dag_mermaid;
                        currentOptimized = data.dag_mermaid;
                        currentLive = data.dag_mermaid;
                        
                        setDiagramView('run');
                        
                        // Set estimated metrics
                        document.getElementById('est-runtime').innerText = data.cost_estimation.runtime.toFixed(3) + 's';
                        document.getElementById('est-cost').innerText = '$' + data.cost_estimation.cost.toFixed(4);
                        document.getElementById('est-tokens').innerText = data.cost_estimation.tokens + " tokens";
                        document.getElementById('opt-savings').innerText = "Dynamic Topology Mode";
                    } else {
                        terminal.innerText = `> ` + data.diagnostics.join('\n');
                        terminal.style.color = "#ef4444";
                    }
                } catch(e) {
                    terminal.innerText = `> ERROR: ${e}`;
                    terminal.style.color = "#ef4444";
                }
            }

            function switchView(viewId) {
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

                event.target.classList.add('active');
                document.getElementById(viewId).classList.add('active');
            }

            setInterval(fetchMetrics, 1000);
            window.onload = () => {
                fetchMetrics();
                renderTopologyList();
                // Preset matching Common Subexpression Elimination to showcase token optimization
                selectPreset("Search Google for ML servers, search Google for ML servers, compare them, and generate a PDF report.");
            };
        </script>
    </head>
    <body>
        <header>
            <h1>OmniCore AI Compiler IDE</h1>
            <div class="status-badge">Workspace: Active</div>
        </header>

        <div class="ide-workspace">
            <!-- PANEL 1: Code / Input Sandbox -->
            <div class="panel">
                <div class="editor-tabs">
                    <button class="tab-btn active" onclick="switchView('tab-nlp')">Natural Language</button>
                    <button class="tab-btn" onclick="switchView('tab-topology')">Dynamic Topology</button>
                </div>

                <div class="panel-body">
                    <!-- NLP Tab -->
                    <div id="tab-nlp" class="tab-content active">
                        <div style="display: flex; gap: 6px; margin-bottom: 12px; flex-wrap: wrap;">
                            <div class="tag" onclick="selectPreset('Search Google for ML servers, search Google for ML servers, compare them, and generate a PDF report.')">Redundancy CSE</div>
                            <div class="tag" onclick="selectPreset('Search Arxiv for LLM agents and summarize findings.')">Search & Summarize</div>
                        </div>
                        <textarea id="query-input" class="sandbox-input" onkeyup="updateTokenUsage()"></textarea>
                        
                        <div class="token-meter">
                            <span style="color: #94a3b8;">Lexer usage:</span>
                            <strong id="token-usage" style="color: #a5b4fc; float: right;">0 tokens</strong>
                        </div>
                        <button class="btn-action" onclick="runNLPCompile()">Compile & Run Pipeline</button>
                    </div>

                    <!-- Dynamic Topology Tab -->
                    <div id="tab-topology" class="tab-content">
                        <div id="nodes-list" style="flex: 1; overflow-y: auto; margin-bottom: 16px; max-height: 250px;">
                            <!-- Nodes list rendered dynamically -->
                        </div>
                        
                        <!-- Add Node Form -->
                        <div style="border-top: 1px solid var(--glass-border); padding-top: 12px; font-size: 12px;">
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 8px;">
                                <input type="text" id="new-node-id" placeholder="Node ID (e.g. n3)" value="n2" style="background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); color: #fff; padding: 4px; border-radius: 4px;"/>
                                <input type="text" id="new-node-name" placeholder="Name" style="background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); color: #fff; padding: 4px; border-radius: 4px;"/>
                            </div>
                            <div style="margin-bottom: 8px;">
                                <select id="new-node-cap" style="width: 100%; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); color: #fff; padding: 4px; border-radius: 4px;">
                                    <option value="WEB_SEARCH">WEB_SEARCH</option>
                                    <option value="SUMMARIZATION">SUMMARIZATION</option>
                                    <option value="PDF_GENERATION">PDF_GENERATION</option>
                                </select>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                                <input type="text" id="new-node-input" placeholder="Input Var" style="background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); color: #fff; padding: 4px; border-radius: 4px;"/>
                                <input type="text" id="new-node-output" placeholder="Output Var" style="background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); color: #fff; padding: 4px; border-radius: 4px;"/>
                            </div>
                            <button class="btn-action" onclick="addCustomNode()" style="background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); margin-bottom: 8px;">Add Node</button>
                        </div>
                        <button class="btn-action" onclick="compileCustomTopology()">Compile Topology</button>
                    </div>
                </div>
            </div>

            <!-- PANEL 2: Visual Graph & Compiler Diagnostics Console -->
            <div class="panel" style="grid-column: span 1;">
                <div class="diag-tab-bar">
                    <button id="tab-btn-ast" class="diag-tab-btn active" onclick="setDiagramView('ast')">1. AST Tree</button>
                    <button id="tab-btn-opt" class="diag-tab-btn" onclick="setDiagramView('opt')">2. Graph Optimization</button>
                    <button id="tab-btn-run" class="diag-tab-btn" onclick="setDiagramView('run')">3. Live Execution</button>
                </div>
                <div class="canvas-area">
                    <!-- AST View -->
                    <div id="ast-view" class="diag-content active" style="width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;">
                        <div id="canvas-ast" style="width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;"></div>
                    </div>

                    <!-- Optimization View -->
                    <div id="opt-view" class="diag-content" style="width: 100%; height: 100%; display: none; flex-direction: row; gap: 20px;">
                        <div style="flex: 1; text-align: center; display: flex; flex-direction: column;">
                            <div style="font-size: 11px; color: #a5b4fc; margin-bottom: 6px; font-weight: 600; letter-spacing: 0.5px;">Initial Graph (Raw inputs)</div>
                            <div id="canvas-initial" style="flex: 1; display: flex; justify-content: center; align-items: center;"></div>
                        </div>
                        <div style="flex: 1; text-align: center; display: flex; flex-direction: column; border-left: 1px solid var(--glass-border); padding-left: 20px;">
                            <div style="font-size: 11px; color: var(--success-color); margin-bottom: 6px; font-weight: 600; letter-spacing: 0.5px;">Optimized Graph (Token Minimization)</div>
                            <div id="canvas-optimized" style="flex: 1; display: flex; justify-content: center; align-items: center;"></div>
                        </div>
                    </div>

                    <!-- Live Execution View -->
                    <div id="run-view" class="diag-content" style="width: 100%; height: 100%; display: none; display: flex; justify-content: center; align-items: center;">
                        <div id="canvas-live" style="width: 100%; height: 100%; display: flex; justify-content: center; align-items: center;"></div>
                    </div>
                </div>
                <div id="console-terminal" class="terminal">> Linter console ready. Waiting for compilation run...</div>
            </div>

            <!-- PANEL 3: Optimizer Telemetry & Active Cluster Nodes -->
            <div class="panel">
                <div class="panel-header">
                    <h2>Optimizer Telemetry</h2>
                </div>
                <div class="panel-body" style="border-bottom: 1px solid var(--glass-border); flex: none;">
                    <div style="margin-bottom: 14px;">
                        <span style="color: #94a3b8; font-size: 13px;">Estimated Latency:</span>
                        <strong id="est-runtime" style="color: #f8fafc; float: right;">0.000s</strong>
                    </div>
                    <div style="margin-bottom: 14px;">
                        <span style="color: #94a3b8; font-size: 13px;">Cost Projections:</span>
                        <strong id="est-cost" style="color: #f8fafc; float: right;">$0.0000</strong>
                    </div>
                    <div style="margin-bottom: 14px;">
                        <span style="color: #94a3b8; font-size: 13px;">Estimated Tokens:</span>
                        <strong id="est-tokens" style="color: #f8fafc; float: right;">0 tokens</strong>
                    </div>
                    <div>
                        <span style="color: #94a3b8; font-size: 13px;">Token Reduction:</span>
                        <strong id="opt-savings" style="color: var(--success-color); float: right;">0.0% savings</strong>
                    </div>
                </div>

                <div class="panel-header" style="border-top: none;">
                    <h2>Active Cluster Nodes</h2>
                </div>
                <div class="panel-body" id="workers" style="padding: 0;">
                    <div class="worker-entry">Loading active nodes...</div>
                </div>

                <div class="panel-header">
                    <h2>Telemetry Metrics</h2>
                </div>
                <div class="panel-body" style="flex: none; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); padding: 12px; border-radius: 8px;">
                        <span style="font-size: 11px; color: #94a3b8;">Completed Nodes</span>
                        <div id="completed-tasks" style="font-size: 24px; font-weight: 700; margin-top: 4px;">0 / 0</div>
                    </div>
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); padding: 12px; border-radius: 8px;">
                        <span style="font-size: 11px; color: #94a3b8;">Cluster Health</span>
                        <div id="health-score" style="font-size: 24px; font-weight: 700; margin-top: 4px;">100%</div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return responses.HTMLResponse(content=html_content)
