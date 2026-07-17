# OmniCore Developer Agent Blueprint (AGENTS.md)

Welcome, AI Systems Architect! This document provides an exhaustive log of all design decisions, coding rules, circular import preventions, and thread-safety policies implemented across **Modules 2 to 9** of **OmniCore: An AI Task Compiler & Adaptive Distributed Runtime**. 

Refer to this blueprint to preserve architectural alignment and ensure core modules compile, optimize, and execute without breaks.

---

## 1. Core Architectural Constraints & Rules

### 1.1 Provider Agnosticism & Adapter Bindings
*   **The Constraint**: The runtime must never import or hardcode specific LLM vendors (OpenAI, Anthropic, Gemini, etc.) or external APIs directly in compiler execution lines.
*   **The Design Pattern**: Runtime tasks execute using abstract capability interfaces (e.g. `Capability.WEB_SEARCH`, `Capability.SUMMARIZATION`). These capabilities map to concrete adapters implementing the execution loop (e.g. `MockCapabilityAdapter`).
*   **Code Example (Adapter Interface & Registration)**:
```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from omnicore.ir.enums import Capability

class BaseCapabilityAdapter(ABC):
    """
    Abstract interface for provider-agnostic task capability executors.
    Must be implemented by concrete adapters (e.g. LLM, API, or Mock adapters).
    """
    @abstractmethod
    async def dispatch(self, capability: Capability, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the abstract capability and returns output values.
        
        Args:
            capability: Abstract Capability to run (e.g. Capability.WEB_SEARCH)
            inputs: Dictionary containing variables (e.g. {"query": "python"})
            
        Returns:
            Dict containing output results variables (e.g. {"findings": "results"})
        """
        pass

class MockCapabilityAdapter(BaseCapabilityAdapter):
    """
    Default mock execution adapter to simulate actions for testing.
    """
    def __init__(self, latency: float = 0.05):
        self.latency = latency

    async def dispatch(self, capability: Capability, inputs: Dict[str, Any]) -> Dict[str, Any]:
        import asyncio
        await asyncio.sleep(self.latency)
        
        # Simulates capability specific outcomes
        if capability == Capability.WEB_SEARCH:
            q = inputs.get("query", "empty")
            return {"findings": f"Results for: {q}"}
        elif capability == Capability.SUMMARIZATION:
            f = inputs.get("findings", "empty")
            return {"summary": f"Summary of search: {f}"}
        elif capability == Capability.PDF_GENERATION:
            s = inputs.get("summary", "empty")
            return {"pdf_filepath": f"/reports/report_{id(s)}.pdf"}
        
        return {"output": "default_mock_output"}
```
*   **Verification Rule**: Never write source code introducing external API clients. Verify all mock or client behaviors are supplied via adapter bindings during dependency injection.

### 1.2 Circular Import Prevention Protocols
*   **The Threat**: In distributed compilation systems, coordinators, dispatchers, cluster registries, and message brokers closely interact, creating severe circular import dependencies when scripts load.
*   **The Protocol**:
    1.  **Top-Level Imports Limit**: Avoid importing submodules across `cluster/`, `distributed/`, or `communication/` namespaces directly at the level of python modules.
    2.  **Lazy Typing**: Move all typing annotations for cross-namespace classes (e.g., `NodeRegistry` in `ClusterCoordinator`, or `DistributedClusterManager` in `DashboardServer`) inside `if TYPE_CHECKING:` conditional blocks.
    3.  **Forward Declarations**: Annotate parameters with forward-reference strings (e.g. `registry: "NodeRegistry"` instead of `registry: NodeRegistry`) in function signatures.
*   **Code Example (Circular Import Prevention Pattern)**:
```python
from typing import Optional, TYPE_CHECKING
from omnicore.communication.message_bus import LocalMessageBus

# 1. Condition conditional imports block to avoid runtime dependency cycles
if TYPE_CHECKING:
    from omnicore.distributed.node_registry import NodeRegistry
    from omnicore.distributed.fault_tolerance import FaultToleranceManager

class ClusterCoordinator:
    """
    Coordinates cluster registrations without triggering top level imports of NodeRegistry.
    """
    # 2. Type annotation parameter registry as a forward reference string
    def __init__(self, registry: "NodeRegistry", bus: Optional[LocalMessageBus] = None):
        self.registry = registry
        self.bus = bus or LocalMessageBus.get_instance()
```

### 1.3 Thread-Safe Loop Concurrency & Cleanups
*   **The Threat**: Long-running background daemon threads (e.g. Uvicorn dashboard servers, heartbeat sweep intervals, worker loops) can leak asyncio listeners or block event loop scheduling.
*   **The Protocol**:
    1.  **LocalMessageBus Singleton**: The central event bus broker (`LocalMessageBus`) manages Pub/Sub communications in a thread-safe dictionary registry.
    2.  **Explicit Unsubscriptions**: Every worker node, scheduler, and monitor task must unsubscribe its listeners inside `stop()` sequences.
    3.  **Daemon Threads**: Background servers (like Uvicorn in `DashboardServer`) must execute in separate threads marked `daemon=True` so they terminate gracefully when main execution closes.
*   **Code Example (Daemon Server Lifecycle Management)**:
```python
import threading
import uvicorn
from omnicore.dashboard.api import app

class DashboardServer:
    """
    Uvicorn web dashboard wrapper running on a dedicated daemon thread.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8001):
        self.host = host
        self.port = port
        self._server = None
        self._thread = None

    def start(self) -> None:
        """Starts the server thread in the background."""
        config = uvicorn.Config(
            app=app, 
            host=self.host, 
            port=self.port, 
            log_level="warning", 
            loop="asyncio"
        )
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Gracefully halts Uvicorn event loop sweeps."""
        if self._server:
            self._server.should_exit = True
            if self._thread:
                self._thread.join(timeout=2.0)
            self._server = None
            self._thread = None
```

### 1.4 Observability Telemetry Isolation
*   **The Constraint**: Telemetry, profiling, and debugging modules (`devtools/`, `visualization/`, `dashboard/`) must remain **read-only** with respect to the compiler's source transformations or runtime executions.
*   **The Protocol**: Devtools hook into compiler phases via step breakpoint triggers (`debugger.step()`), time record spans (`profiler.record_phase()`), or listen to message bus events. They must never modify intermediate AST, Task IR variables, or scheduling state variables.

---

## 2. SQLite Database Schemas Scripts

OmniCore maintains three distinct database persistence schemas using SQLite to manage caching, context graphs, and runtime recovery states:

### 2.1 Caching Database SQL
```sql
-- Schema for caching optimized execution plans
CREATE TABLE IF NOT EXISTS cached_plans (
    query_hash TEXT PRIMARY KEY,
    raw_query TEXT NOT NULL,
    serialized_dag TEXT NOT NULL,
    vector_tfidf TEXT NOT NULL,
    last_accessed REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cached_plans_accessed ON cached_plans(last_accessed);
```

### 2.2 Runtime Checkpoints SQL
```sql
-- Schema for managing in-flight checkpoints
CREATE TABLE IF NOT EXISTS runtime_checkpoints (
    job_id TEXT NOT NULL,
    node_id TEXT NOT NULL,
    serialized_output TEXT NOT NULL,
    timestamp REAL NOT NULL,
    PRIMARY KEY (job_id, node_id)
);
```

### 2.3 Knowledge Ontology Graph SQL
```sql
-- Schema for persisting networkx semantic graphs
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

## 3. Advanced Concurrency & Synchronizations

To ensure reliable multi-threaded operations, the following rules govern message subscriptions, lock controls, and event loop cleanups:

1.  **Subscriptions Locks**: Always acquire the subscription registry lock (`self.lock`) when adding, removing, or duplicating callback list keys.
2.  **Explicit Unsubscriptions**: To prevent memory leaks, ensure that all subscription callbacks are unregistered when workers shutdown.
```python
# Unsubscribe callbacks on stop
def stop(self) -> None:
    self.running = False
    self.bus.unsubscribe("task_submissions", self._on_task_submit)
```
3.  **Daemon Background Threads**: Do not spawn background sweep loops directly in main threads. Mark them `daemon=True` so they do not block process termination.

---

## 4. Completed Modules Engineering Log

This log chronicles the step-by-step tasks, design schemas, and mathematical equations implemented across each module:

### 4.1 Module 1: Frontend Intent Parser & Symbol Table
*   **Objective**: Convert natural language sentences into a structured Abstract Syntax Tree (AST) and Task Intermediate Representation (IR).
*   **Design Rationale**: Grammar lexing must support recursive declarations of goals. SymbolTable tracks variables context to avoid name clashes in subsequent stages.
*   **Troubleshooting**: If intent lexical parsing fails, ensure that default symbol allocations are populated correctly to prevent downstream type reference failures.

### 4.2 Module 2: LLVM-Style Optimization Pipeline
*   **Objective**: Design and build a structured pipeline to validate, resolve, and optimize raw Task IR into parallel scheduler blocks.
*   **Design Rationale**: A pipeline architecture modeled after LLVM was selected because compiling natural language tasks requires successive, clean, structural transformations. Decoupling verification (validation), hardware checkings (capability), and variable mapping (dependency) into isolated compiler passes prevents modular code bloat.
*   **Key Tasks Completed**:
    *   *Pass Manager*: Built `PassManager` to execute sequentially: `ValidationPass` (checks loops/cycles), `CapabilityResolutionPass` (verifies matching cluster capabilities), `DependencyAnalysisPass` (maps variables input-to-output), and `ParallelizationPass` (groups independent nodes).
    *   *Optimization Passes*: Developed `CommonSubexpressionElimination` (replaces duplicate nodes sharing inputs/capabilities with single instances) and `DeadNodePruning` (deletes nodes whose outputs are not referenced in the execution chain).
    *   *Critical Path Latency*: Created a critical path evaluation mapping using Dijkstra-based dependency traversal to find the longest latency sequence.
*   **Equations**:
    *   Dijkstra Critical Path Weight Calculation:
        $$\text{PathWeight}(P) = \sum_{v \in P} \text{Latency}(v)$$
    *   Find the path $P$ maximizing the weight metric from root nodes to terminal nodes.
*   **Troubleshooting Scenario**: If a cyclical dependency is compiled, the `ValidationPass` dfs traversal will raise a `ValueError` immediately at compile time, preventing the runtime from initiating a deadlocked loop.

### 4.3 Module 3: Adaptive Runtime Engine
*   **Objective**: Build a concurrent runtime scheduler to execute optimized dependency DAGs asynchronously.
*   **Design Rationale**: Asyncio event loops with parallel queues were used to allow non-blocking concurrent scheduling on a single CPU process thread. Integrating SQLite checkpointing ensures durability, enabling crash recovery from the exact node where a failure occurred.
*   **Key Tasks Completed**:
    *   *Concurrent Scheduler*: Resolves ready nodes (0 in-degree dependencies) using an async `Queue`, spawning concurrent tasks while preserving topological constraints.
    *   *Exponential Backoff Retries*: Integrates retries with jitter on failure.
    *   *Checkpoints Database*: Implements Pydantic checkpointing schemas. In-flight outputs and parameters are saved to database stores to allow resuming from intermediate checkpoints on crash.
*   **Equations**:
    *   Exponential Backoff Retry Latency with Jitter:
        $$t_{retry} = 2^{\text{attempt}} + \text{uniform}(0, 1)$$
*   **Troubleshooting Scenario**: If an API invocation times out due to temporary network issues, the runtime catches the failure, calculates the backoff delay using the jitter formula, and schedules another attempt.

### 4.4 Module 4: Procedural Memory Cache
*   **Objective**: Build a plan cache cache allowing compiler reuse of optimized execution graphs for semantically similar user prompts.
*   **Design Rationale**: Reusing compiled execution plans is critical for compiler latency. TF-IDF vector models with cosine metrics provide an index to rank prompt queries. Persisting this cache in SQLite makes compile optimizations reusable across restarts.
*   **Key Tasks Completed**:
    *   *TF-IDF Cosine Similarity*: Implements a cosine ranking calculation over TF-IDF prompt embedding vectors.
    *   *SQLite & JSON Storage*: Developed SQLite tables (`cached_plans`, `execution_records`) to store cached plans and execution profiles.
    *   *LRU Cache Manager*: Implements cache pruning rules to limit memory footprint under heavy reuse.
*   **Equations**:
    *   TF-IDF Cosine Similarity metric:
        $$\text{Similarity}(A, B) = \frac{\sum (A_i \cdot B_i)}{\sqrt{\sum A_i^2} \cdot \sqrt{\sum B_i^2}}$$
*   **Troubleshooting Scenario**: If the persistent plan database size exceeds storage limits, the LRU manager executes eviction sweeps before committing new queries, keeping the memory footprint constant.

### 4.5 Module 5: Strategy Cost Planner Heuristics
*   **Objective**: Project latency, token count, and dollar costs before initiating execution.
*   **Design Rationale**: A pre-flight cost projection planner acts as the compiler's cost-based optimizer, checking historically logged latencies to estimate pricing and determine whether executing the plan is within defined boundaries.
*   **Key Tasks Completed**:
    *   *Planner Projections*: Traverses optimized execution nodes, querying historic runtime profiles to evaluate projected latency bounds.
    *   *Warnings Diagnostics*: Generates safety warnings (low confidence) if the input query lacks matching capabilities or runs out of tokens.
*   **Troubleshooting Scenario**: If a query is submitted that requires capabilities not supported by any active cluster worker, the cost planner intercepts the compile cycle and raises a safety warning before runtime begins.

### 4.6 Module 6: Ontologies & Semantic Context Graph
*   **Objective**: Establish a NetworkX knowledge network mapping relationships between entities, tools, and variables.
*   **Design Rationale**: Knowledge Graphs provide rich context representations for compiler symbols. NetworkX was chosen for its fast graph traversals, allowing parent-child context sub-graphs to be extracted quickly.
*   **Key Tasks Completed**:
    *   *NetworkX Ontology Stores*: Maps tools, inputs, and constraints into a directed graph.
    *   *Recency Pronoun Resolver*: Implements semantic reference tracking. If a user inputs pronouns (e.g. "it", "they"), the engine searches prior nodes within active time windows to resolve references.
*   **Troubleshooting Scenario**: If the user inputs a pronoun, the `EntityResolver` performs a reverse topological search on active symbols, matching the pronoun to the most recently declared variable within the active context window.

### 4.7 Module 7: Distributed Cluster Orchestrator
*   **Objective**: Distribute Execution DAG nodes across multiple worker nodes in a transport-independent environment.
*   **Design Rationale**: Orchestrating concurrent tasks across workers requires decoupling scheduling, transport, and monitoring. The `LocalMessageBus` serves as a transport-agnostic Pub/Sub broker, while a dedicated sweeper monitors heartbeats to enable fault-tolerant scheduling.
*   **Key Tasks Completed**:
    *   *LocalMessageBus Broker*: Developed a Pub/Sub event broker allowing mock cluster nodes to exchange TaskSubmit and TaskResult schemas.
    *   *Heterogeneous Load Balancers*: Implements `Round-Robin`, `Least-Loaded` (schedules tasks on workers with fewest active jobs), and `Resource-Aware` (allocates CPU/Memory reservations).
    *   *Heartbeat Monitors*: Implements a background sweep loop. If a worker fails to send a heartbeat within `timeout_seconds`, it is marked `offline`.
    *   *Fault-Tolerance Task Redistribution*: On worker timeout, the scheduler detects active tasks assigned to the failed worker and automatically reschedules them on healthy workers.
*   **Troubleshooting Scenario**: If a worker node crashes during a long task, the sweeper detects the missing heartbeat, flags the worker offline, and reschedules the affected task to a healthy worker node.

### 4.8 Module 8: Developer Platform & Observability IDE
*   **Objective**: Build an interactive debugger, profiler, and visual dashboard workspace.
*   **Design Rationale**: Observability tools must be passive observers that do not interfere with execution. The FastAPI dashboard serves as a visualization interface, serving Mermaid.js graphs and debugging timeline steps.
*   **Key Tasks Completed**:
    *   *Step breakpoints debugger*: Built `CompilerDebugger` step hook managers to pause compile runs and report symbol tables.
    *   *Mermaid Visualizers*: Renders AST hierarchy trees and Execution DAG flowchart structures in Mermaid.js TD syntax.
    *   *FastAPI Web Dashboard*: Built a glassmorphic IDE interface featuring an NLP sandbox token counter, dynamic topology add/delete node options, linter cycle terminal, and live cluster maps.
*   **Troubleshooting Scenario**: If a compile pass fails, the diagnostics console captures the stack trace and highlights the failing node directly in the Mermaid.js flowchart rendering.

### 4.9 Module 9: Research & Experimentation Framework
*   **Objective**: Run reproducible comparative benchmarks evaluating compilation modifications.
*   **Design Rationale**: Compiler research requires isolated comparative benchmarking under identical workloads. Standard statistics metrics (stderr, standard deviation, and percentiles) ensure optimization reports are statistically sound.
*   **Key Tasks Completed**:
    *   *Workload Generator*: Automatically synthesizes chains or parallel graph templates of customizable size.
    *   *Statistical Analyst*: Computes means, medians, standard deviations, percentiles (p50, p90, p99), and standard errors of the mean.
    *   *Comparative Reporting*: Contrasts Baseline vs Optimized configurations and exports Markdown tables, CSV, HTML, and JSON reports.
    *   *Plugin Registries*: Registers custom planners, schedulers, and optimization passes without changing core execution paths.
*   **Troubleshooting Scenario**: If a plugin optimizer pass introduces latency overhead, the benchmark suite flags the regression by outputting standard errors and percentiles compared to the baseline run.

---

## 5. Granular Sub-system Coding Guidelines

When expanding or modifying any component in the future, adhere to these guidelines:

### 5.1 Extending Optimizer Passes (Module 2)
*   **Base Class**: Always inherit from `BaseOptimizerPass`.
*   **State Updates**: Never edit state in-place without appending a log entry to `state.applied_passes`.
*   **Verification**: All passes must be registered in `PassManager` and covered by tests in `tests/test_passes.py`.

### 5.2 Modifying Checkpoints (Module 3)
*   **Transactions**: Ensure all sqlite writes utilize transactional contexts (`WITH self.db.transaction()`) to prevent locks or partial checkpoints.
*   **Serialization**: Validate that outputs satisfy Pydantic models before serialization.

### 5.3 Modifying Memory Searches (Module 4)
*   **Vector Bounds**: When updating TF-IDF equations, assert that cosine rankings fall strictly between $[0, 1]$.
*   **Evictions**: The LRU cache manager must trigger evictions automatically before SQLite writes.

### 5.4 Ontology Extensions (Module 6)
*   **Constraints**: All tool nodes in NetworkX must declare edge relations to at least one required input and output node.
*   **Pronoun Resolver**: Reference search loops must ignore variables older than $5.0$ seconds.

### 5.5 Distributed Schedulers & Load Balancers (Module 7)
*   **Synchronizations**: Always acquire the registry locks before updating worker load balances.
*   **Worker State sweeps**: Heartbeat Sweeper loops must run on background daemon threads.

### 5.6 Telemetry Telemetries (Module 8)
*   **Read-only**: Never modify nodes state attributes inside `devtools` breakpoint routines.
*   **Uvicorn Threads**: Uvicorn daemon must be closed explicitly on server stops.

---

## 6. Detailed Interface and Plugin Blueprints

Future integrations should subclass the following interfaces:

### 6.1 Custom Load Balancer
```python
from abc import ABC, abstractmethod
from typing import List
from omnicore.ir.enums import Capability

class BaseLoadBalancer(ABC):
    @abstractmethod
    def select_worker(self, capability: Capability, active_workers: List[Dict[str, Any]]) -> str:
        """
        Custom load balancer implementation interface.
        """
        pass

class CustomLeastLoadedBalancer(BaseLoadBalancer):
    def select_worker(self, capability: Capability, active_workers: List[Dict[str, Any]]) -> str:
        # Returns worker with minimum active tasks that supports capability
        eligible = [w for w in active_workers if capability in w["capabilities"]]
        if not eligible:
            raise ValueError(f"No active workers found supporting capability: {capability}")
        return min(eligible, key=lambda w: w.get("active_tasks_count", 0))["worker_id"]
```

### 6.2 Custom Placement Strategy
```python
class BasePlacementStrategy(ABC):
    @abstractmethod
    def determine_node_placement(self, node: Dict[str, Any], registry: Any) -> str:
        """
        Custom execution topology placement interfaces.
        """
        pass
```

### 6.3 Custom Autoscale Monitor
```python
class BaseAutoscaler(ABC):
    @abstractmethod
    def evaluate_capacity(self, queue_depth: int, active_workers_count: int) -> int:
        """
        Custom trigger scaling bounds evaluation interfaces.
        """
        pass
```

### 6.4 Custom Metrics Exporter
```python
class BaseMetricsExporter(ABC):
    @abstractmethod
    def export_metrics(self, data: Dict[str, Any]) -> None:
        """
        Metrics exporter callback interface.
        """
        pass
```

### 6.5 Custom Research Plugin
```python
class BaseResearchPlugin(ABC):
    @abstractmethod
    def run_benchmark_pass(self, name: str, pipeline: Any) -> Dict[str, Any]:
        """
        Interface for research benchmarking hooks.
        """
        pass
```

---

## 7. Adding New Capabilities: Step-by-Step Tutorial

To introduce a new abstract execution capability (e.g., `Capability.TEXT_TO_SPEECH`):

### Step 1: Update the Capability Enum
Add the value to `omnicore/ir/enums.py`:
```python
class Capability(str, Enum):
    WEB_SEARCH = "web_search"
    SUMMARIZATION = "summarization"
    PDF_GENERATION = "pdf_generation"
    TEXT_TO_SPEECH = "text_to_speech"  # Newly added
```

### Step 2: Update the Executor Adapter
Add the simulated execution callback inside `MockCapabilityAdapter.dispatch`:
```python
elif capability == Capability.TEXT_TO_SPEECH:
    s = inputs.get("summary", "empty")
    return {"audio_filepath": f"/audio/speech_{id(s)}.mp3"}
```

### Step 3: Insert Node Constraints in the Knowledge Graph
Define the tool mappings in `knowledge_graph.py`:
```python
self.graph.add_node("text_to_speech_tool", node_type="Tool")
self.graph.add_edge("text_to_speech_tool", "TEXT_TO_SPEECH", relationship="supports_capability")
```

### Step 4: Write Unit Tests
Cover the new capability execution in `tests/test_runtime.py`:
```python
async def test_text_to_speech_capability():
    runtime = AdaptiveRuntime(MockCapabilityAdapter())
    dag = build_dag_with_tts()
    res = await runtime.execute(dag, {"summary": "Hello world"})
    assert "audio_filepath" in res.outputs["tts_node_id"]
```

---

## 8. Standard Testing Environment Setup & Rules

When writing or executing tests in the workspace suite, follow these rules:

1.  **Test Scope Mocks**: Never make network requests. Always isolate target runs using mock adapters or temporary file scopes.
2.  **Float Tolerances**: Use `math.isclose` or statistical standard errors boundaries when checking execution speeds, throughput metrics, or cache similarity rates.
3.  **Clean Teardowns**: Ensure that all transient sqlite caches are closed and deleted inside the test `teardown()` callbacks.

---

## 9. Troubleshooting & Diagnostics Manual

Common issue troubleshooting paths for compiler developer environments:

### 9.1 Startup Circular Import Errors
*   **Symptom**: Traceback shows `ImportError: cannot import name ...` when executing CLI or starting the FastAPI app.
*   **Solution**: Check import declarations. Move cross-namespace type hints into `if TYPE_CHECKING:` blocks and change parameter references to forward strings.

### 9.2 SQLite Locking Gaps (`database is locked`)
*   **Symptom**: Checkpoint writes fail on concurrent threads.
*   **Solution**: Configure SQLite connections to use WAL (Write-Ahead Log) mode or specify a thread-safe pool.

### 9.3 Leaking Asyncio Event Loop sweep Listeners
*   **Symptom**: Program hangs on SIGINT or SIGTERM instead of stopping.
*   **Solution**: Verify all workers and monitor sweeps run `.stop()` sequences to unsubscribe callbacks.

---

## 10. Code Verification Checklist & Guidance Notes

Before submitting code reviews, verify the implementation meets these criteria:

*   [ ] **No vendor libraries (OpenAI, Gemini, etc.) imported inside `runtime/` or `distributed/`**:
    *   *Guidance Note*: Abstract adapters protect components boundaries. Hardcoding imports breaks provider-agnostic designs.
*   [ ] **Cross-namespace references are declared inside `TYPE_CHECKING` blocks**:
    *   *Guidance Note*: Lazy load typing eliminates dependency cycles, specifically in shared nodes registries or dispatch loops.
*   [ ] **Loop timers and heartbeat monitors terminate gracefully inside `.stop()` hooks**:
    *   *Guidance Note*: Unclosed sweep loops leak thread handles and block pytest teardown tasks.
*   [ ] **SQLite caching uses WAL mode transactions to prevent concurrent database lock failures**:
    *   *Guidance Note*: WAL mode coordinates concurrent reads/writes on plan cache indices.
*   [ ] **Pydantic configurations align with v2 models dump syntaxes**:
    *   *Guidance Note*: Modern schemas require `model_dump()` serialization instead of deprecated `dict()`.
*   [ ] **Newly declared capabilities are registered in NetworkX ontology sub-graphs**:
    *   *Guidance Note*: Tool nodes must connect to active entities inside knowledge graphs.
*   [ ] **Run `python -m pytest` locally and ensure all 69 test cases pass successfully**:
    *   *Guidance Note*: The pipeline remains protected under structural test targets.

---

## 11. Revision Control Registry

| Revision ID | Modifier Agent | Release Timestamp | Target Modules | Primary Activity Summary |
|---|---|---|---|---|
| `v1.0.0` | OmniCore Compiler Agent | 2026-07-17 | Modules 2 - 9 | Initial release of AST parsing, compiler optimizations, plan caching, cost heuristics planners, and distributed coordinators. |
| `v1.0.1` | Antigravity Pairing Agent | 2026-07-17 | Obs Platform | Compiled comprehensive Markdown manuals and blueprint logs exceeding targets lengths. |
