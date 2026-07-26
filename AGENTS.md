# OmniCore Developer Agent Blueprint (AGENTS.md)

This blueprint documents core architectural constraints, thread-safety guidelines, database schemas, and module specifications for developing and extending **OmniCore**.

---

## 1. Core Architectural Constraints & Rules

### 1.1 Provider Agnosticism & Adapter Bindings
- **Rule**: Never import or hardcode specific vendor LLM clients (OpenAI, Anthropic, Gemini) directly inside compiler or execution lines (`omnicore/runtime/`, `omnicore/distributed/`).
- **Design Pattern**: All task capabilities execute using abstract `Capability` enums (`Capability.WEB_SEARCH`, `Capability.SUMMARIZATION`, etc.) dispatched via concrete capability adapters implementing `BaseCapabilityAdapter` (e.g. `MockCapabilityAdapter`).

### 1.2 Circular Import Prevention
- **Top-Level Imports**: Avoid importing submodules across `cluster/`, `distributed/`, `communication/`, or `dashboard/` namespaces at module top-level.
- **Lazy Typing**: Place cross-namespace typing annotations inside `if TYPE_CHECKING:` blocks.
- **Forward References**: Use string forward declarations (e.g., `registry: "NodeRegistry"`) in function signatures.

### 1.3 Concurrency & Thread Safety
- **Event Bus Singleton**: `LocalMessageBus` is a thread-safe singleton broker. Always acquire internal locks during subscriber modifications.
- **Explicit Unsubscriptions**: Every worker, scheduler, and heartbeat sweeper must unsubscribe listeners inside `.stop()` hooks to avoid leaking handles.
- **Daemon Threads**: Background servers (e.g. Uvicorn in `DashboardServer`) and heartbeat monitoring loops must run on threads with `daemon=True`.

### 1.4 Observability & UI Isolation
- Telemetry, profiling, debugging, visualization tools, and web dashboards (`devtools/`, `visualization/`, `dashboard/`) must remain **read-only** and never modify AST nodes, Task IR variables, or execution DAG states.

---

## 2. Persistence Database Schemas (SQLite)

OmniCore uses SQLite for plan caching, runtime checkpoints, and knowledge graphs:

```sql
-- Caching Database (cached_plans)
CREATE TABLE IF NOT EXISTS cached_plans (
    query_hash TEXT PRIMARY KEY,
    raw_query TEXT NOT NULL,
    serialized_dag TEXT NOT NULL,
    vector_tfidf TEXT NOT NULL,
    last_accessed REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_cached_plans_accessed ON cached_plans(last_accessed);

-- Runtime Checkpoints (runtime_checkpoints)
CREATE TABLE IF NOT EXISTS runtime_checkpoints (
    job_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    serialized_output TEXT NOT NULL,
    timestamp REAL NOT NULL,
    PRIMARY KEY (job_id, node_id)
);

-- Semantic Ontology Graph (ontology_nodes & ontology_edges)
CREATE TABLE IF NOT EXISTS ontology_nodes (
    node_name TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    metadata TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ontology_edges (
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    relationship TEXT NOT NULL,
    timestamp REAL NOT NULL,
    PRIMARY KEY (source, target, relationship)
);
```

---

## 3. Module Architecture Summary

1. **Module 1 (Frontend Parser)**: Natural language to `TaskIR` & `ASTGoal`; Symbol scope resolution (`SymbolTable`).
2. **Module 2 (LLVM Optimizer)**: Sequential optimization passes (`ValidationPass` loop detection, `CapabilityResolutionPass`, `DependencyAnalysisPass`, `CSEPass`, `DeadNodePruningPass`, `ParallelizationPass`) and Dijkstra critical path latency analysis.
3. **Module 3 (Adaptive Runtime)**: Topological queue execution with exponential backoff retry jitter ($t_{retry} = 2^{attempt} + \text{uniform}(0, 1)$) and SQLite node output checkpointing.
4. **Module 4 (Procedural Memory Cache)**: TF-IDF embedding & Cosine Similarity plan retrieval ($\text{Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$) with LRU eviction.
5. **Module 5 (Strategy Cost Planner)**: Pre-flight latency, token count, and dollar cost projection heuristic modeling.
6. **Module 6 (Knowledge Graph)**: NetworkX semantic entity-tool graph & recency-based pronoun resolution (`EntityResolver`).
7. **Module 7 (Distributed Cluster Orchestrator)**: Node registry, load balancers (`Round-Robin`, `Least-Loaded`, `Resource-Aware`), background heartbeat sweeper, and fault-tolerant task redistribution.
8. **Module 8 (Observability IDE & Liquid Glass Web UI)**: FastAPI server, Uvicorn daemon, step breakpoints (`CompilerDebugger`), Mermaid.js diagram visualizers, and React + TypeScript + Tailwind CSS Liquid Glass UI (`omnicore/dashboard/frontend/` -> `dist/`).
9. **Module 9 (Research Framework)**: Synthetic DAG workload generator, statistical analysis (means, medians, stddev, percentiles), and comparative markdown/HTML reporting.

---

## 4. Subsystem Extension Guidelines

### 4.1 Adding New Capabilities
1. Add new enum value to `Capability` (`omnicore/ir/enums.py`).
2. Implement capability handler in adapter (`omnicore/runtime/adapters/capability_adapter.py`).
3. Map capability node relationship in NetworkX graph (`omnicore/knowledge/knowledge_graph.py`).
4. Add unit test coverage in `tests/test_runtime.py`.

### 4.2 Creating Optimizer Passes
1. Subclass `BaseOptimizerPass` (`omnicore/optimizer/passes/`).
2. Implement `execute(self, state: OptimizerState) -> OptimizerState`. Append pass name to `state.applied_passes`.
3. Register pass in `PassManager` (`omnicore/optimizer/pass_manager.py`).

### 4.3 Custom Load Balancers
1. Implement balancer logic accepting capability and active worker list (`omnicore/distributed/load_balancer.py`).
2. Integrate policy into `PlacementStrategy` (`omnicore/distributed/placement_strategy.py`).

### 4.4 Dashboard UI Modifications
1. React source code lives in `omnicore/dashboard/frontend/src/`.
2. Build bundle with `npm run build` inside `omnicore/dashboard/frontend/` (outputs to `omnicore/dashboard/dist/`).
3. FastAPI (`omnicore/dashboard/api.py`) automatically serves `dist/index.html` at `GET /`, mounts static assets at `/assets`, and serves `graphify-out/graph.html` at `GET /api/graphify_html`.
4. Theme mode is managed via `theme: 'dark' | 'light'` toggling `document.body.className = 'dark-mode' | 'light-mode'`.

### 4.5 Cloud Deployment Manifests
- **Vercel**: Pre-configured via `vercel.json` routing API requests to ASGI serverless handler `api/index.py`.
- **Docker**: Multi-stage `Dockerfile` building Node 20 React dist assets and executing FastAPI via Uvicorn on `$PORT`.


### 4.6 Performance Profiling & Traces
- All pipeline compilation and execution calls in `omnicore/dashboard/api.py` must measure phase durations (`parsing`, `optimization`, `execution`) using `shared_profiler.record_phase()` and record trace spans using `shared_tracer.start_span()` and `shared_tracer.end_span()`.

---

## 5. Verification Checklist

Before committing changes, ensure:
- [ ] No direct vendor LLM client imports in `runtime/` or `distributed/`.
- [ ] Cross-namespace references use `if TYPE_CHECKING:` and forward strings.
- [ ] Sweep loops and server daemon threads stop cleanly inside `.stop()`.
- [ ] Frontend changes are built to `omnicore/dashboard/dist` via `npm run build`.
- [ ] All 13 test suites pass (`python -m pytest`).

