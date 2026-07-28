# Graph Report - AI_taskIR  (2026-07-28)

## Corpus Check
- 204 files · ~49,103 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1563 nodes · 4304 edges · 76 communities (68 shown, 8 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 637 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dde9a98e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- passes.py
- test_planner.py
- Capability
- DistributedClusterManager
- OptimizedExecutionDAG
- test_knowledge.py
- devDependencies
- ExecutionGraph
- AdaptiveRuntime
- SQLiteGraphStore
- Diagnostic
- App.tsx
- ClusterWorker
- RuntimeNodeStatus
- graph_manager.py
- ProceduralMemory
- cluster_manager.py
- KnowledgeGraph
- CachedPlan
- devtools_example.py
- runtime/__init__.py
- devtools/__init__.py
- ExecutionRecord
- api.py
- compilerOptions
- NodeRegistry
- test_memory.py
- RuntimeState
- IntentParser
- LocalMessageBus
- compilerOptions
- DistributedScheduler
- ReportGenerator
- RuntimeMetricsTracker
- test_research.py
- test_devtools.py
- RelationshipEngine
- PassManager
- PluginRegistry
- RuntimeContext
- Tracer
- SQLiteStore
- HeartbeatMonitor
- PlanLRUCache
- JSONStore
- ClusterCoordinator
- CompilerDebugger
- BenchmarkRunner
- .run_experiment
- PlanRepository
- MemoryMetricsTracker
- FaultToleranceManager
- .has_cycle
- api_example.py
- .has_node
- .visualize
- GraphDiagnostic
- DevToolsError
- .get_parallel_groups
- ExperimentError
- .execute
- optimize_example.py
- tsconfig.json
- KnowledgeManager
- .get_statistics
- CapabilityProfile
- BenchmarkRunner
- omnicore
- workflows/graphify.md
- SQLiteGraphStore
- OntologyEntity
- ContextEngine
- ExperimentError
- .should_retry
- PassManager

## God Nodes (most connected - your core abstractions)
1. `Capability` - 117 edges
2. `TaskIR` - 104 edges
3. `OptimizedExecutionDAG` - 92 edges
4. `Dependency` - 63 edges
5. `IntentParser` - 60 edges
6. `OptimizedExecutionNode` - 58 edges
7. `ExecutionNode` - 56 edges
8. `TaskOptimizer` - 56 edges
9. `ExecutionDAG` - 55 edges
10. `CachedPlan` - 51 edges

## Surprising Connections (you probably didn't know these)
- `ParseRequest` --uses--> `ExecutionDAG`  [INFERRED]
  examples/api_example.py → omnicore/ir/models.py
- `ParseRequest` --uses--> `TaskIR`  [INFERRED]
  examples/api_example.py → omnicore/ir/models.py
- `ParseResponse` --uses--> `ExecutionDAG`  [INFERRED]
  examples/api_example.py → omnicore/ir/models.py
- `ParseResponse` --uses--> `TaskIR`  [INFERRED]
  examples/api_example.py → omnicore/ir/models.py
- `ParseRequest` --uses--> `CompileError`  [INFERRED]
  examples/api_example.py → omnicore/parser/intent_parser.py

## Import Cycles
- None detected.

## Communities (76 total, 8 thin omitted)

### Community 0 - "passes.py"
Cohesion: 0.13
Nodes (27): ASTNode, CommandNode, ConjunctionNode, ParameterNode, ProgramAST, BaseModel, Represents an individual task command or step (e.g., 'Search GitHub for Python c, Represents concurrent execution (e.g. A and B, in parallel). (+19 more)

### Community 1 - "test_planner.py"
Cohesion: 0.05
Nodes (63): main(), run_planning_showcase(), ExecutionStrategy, BaseModel, Enum, str, Execution configuration settings chosen by the planner., StrategyConfig (+55 more)

### Community 2 - "Capability"
Cohesion: 0.23
Nodes (34): PlacementStrategy, Decides load balancer policies based on execution constraints and capability pro, Capability, Complexity, NodeStatus, Enum, str, TaskIntent (+26 more)

### Community 3 - "DistributedClusterManager"
Cohesion: 0.09
Nodes (23): NodeInfo, BaseModel, Metadata describing a network node in the cluster., BaseModel, Capacity and active allocations of cluster worker resource limits., Checks if there are sufficient unallocated resources to run the requirement., Requested resources for scheduling and running a task node., ResourceRequirement (+15 more)

### Community 4 - "OptimizedExecutionDAG"
Cohesion: 0.12
Nodes (39): build_dag_from_graph(), Helper function to instantiate an OptimizedExecutionDAG model., OptimizedExecutionDAG, OptimizedExecutionNode, Main entry point orchestrator for the OmniCore Task Optimization Pipeline.     I, Compiles and optimizes the given TaskIR and ExecutionDAG.         Returns a tupl, TaskOptimizer, CapabilityResolutionPass (+31 more)

### Community 5 - "test_knowledge.py"
Cohesion: 0.11
Nodes (25): main(), OntologyValidationError, Raised when data added to the Knowledge Graph violates the ontology constraints., KnowledgeGraphBuilder, Registers all Capability enums with the graph., Registers default taxonomy hierarchies and capability dependencies., Fluent builder class to populate the Knowledge Graph with standard     capabilit, OntologyCapability (+17 more)

### Community 6 - "devDependencies"
Cohesion: 0.05
Nodes (37): lucide-react, mermaid, dependencies, lucide-react, mermaid, react, react-dom, devDependencies (+29 more)

### Community 7 - "ExecutionGraph"
Cohesion: 0.08
Nodes (19): ExecutionGraph, Adds a node to the execution graph., Adds a directed dependency edge from source to target., Looks up a node object by its ID., Returns all execution node objects., Returns all dependency edges as Dependency models., Finds and returns a cycle as a list of edges, if one exists., Wraps a NetworkX directed graph representation of execution nodes and dependency (+11 more)

### Community 8 - "AdaptiveRuntime"
Cohesion: 0.11
Nodes (30): main(), run_end_to_end(), CapabilityAdapter, MockCapabilityAdapter, Simulated implementation of CapabilityAdapter.     Used for local testing and va, Abstract Base Class for all capability execution adapters.     Adapters map abst, BaseModel, Calculates backoff delay for the given retry attempt (1-indexed). (+22 more)

### Community 9 - "SQLiteGraphStore"
Cohesion: 0.15
Nodes (7): GraphStoreInterface, JSONGraphStore, Any, JSON flat-file-backed graph persistence store., Returns List of (node_id, node_type, data) tuples., Returns List of (source_id, target_id, relation_type, data) tuples., Interface for pluggable Knowledge Graph stores.

### Community 10 - "Diagnostic"
Cohesion: 0.15
Nodes (25): CycleError, OptimizerError, ValueError, Raised when a dependency cycle is detected in the execution graph., Base exception for all optimization-related errors., Raised when the input task IR or execution graph fails validation checks., ValidationError, Diagnostic (+17 more)

### Community 11 - "App.tsx"
Cohesion: 0.06
Nodes (39): TAB_TITLES, DiagramCanvas(), DiagramCanvasProps, viewMeta, ViewMode, views, GraphifyViewer(), clampZoom() (+31 more)

### Community 12 - "ClusterWorker"
Cohesion: 0.15
Nodes (17): BrokenWorker, ClusterWorker, Worker that silent-fails or drops tasks for fault-tolerance checks., Cluster worker node that advertises resources, listens for dispatched tasks,, Starts worker heartbeat loops and registers with coordinator., Stops worker health loops and unsubscribes from broker., Periodically publishes worker heartbeat status signals., Processes and executes a task payload. (+9 more)

### Community 13 - "RuntimeNodeStatus"
Cohesion: 0.13
Nodes (22): ExecutionNodeState, BaseModel, Enum, str, Tracks runtime execution state and statistics for a single node., RuntimeNodeStatus, ExecutionPlan, BaseModel (+14 more)

### Community 14 - "graph_manager.py"
Cohesion: 0.08
Nodes (19): GraphDiagnostic, GraphDiagnosticSeverity, BaseModel, Enum, str, Diagnostic report for Knowledge Graph consistency checks., KnowledgeError, ValueError (+11 more)

### Community 15 - "ProceduralMemory"
Cohesion: 0.11
Nodes (14): main(), MemoryManager, Any, Integrates the Front-end Compiler, Graph Optimizer, and Procedural Memory.     A, Runs front-end compilation to retrieve the TaskIR, then searches procedural memo, Creates and stores an ExecutionRecord log entry after running a plan in the runt, ProceduralMemory, Any (+6 more)

### Community 16 - "cluster_manager.py"
Cohesion: 0.09
Nodes (24): Autoscaler, Any, Decides when to trigger worker scale-up or scale-down events based on queue dept, ClusterDiagnostics, Any, Logs scheduling timeline events, bottlenecks, and worker offline warnings., ClusterError, ValueError (+16 more)

### Community 17 - "KnowledgeGraph"
Cohesion: 0.12
Nodes (11): Saves a semantic entity node to the graph and store., KnowledgeGraph, Wraps a NetworkX directed graph to store semantic concepts (capabilities, entiti, Loads and syncs in-memory NetworkX state from the store., Removes a node and its edges from the graph and store., Removes a relationship from the graph and store., OntologyEntity, BaseModel (+3 more)

### Community 18 - "CachedPlan"
Cohesion: 0.10
Nodes (35): MemoryError, ValueError, Raised when a plan is incompatible due to version changes., Base exception for all procedural memory errors., VersionMismatchError, rank_plans(), Computes a quality score between 0.0 and 1.0 for a plan candidate.     Factors:, Ranks plan candidates.     Returns a sorted list of (CachedPlan, rank_score) tup (+27 more)

### Community 19 - "devtools_example.py"
Cohesion: 0.15
Nodes (7): PerformanceProfiler, Any, Records time spent in a specific compiler/runtime phase., Compiles a detailed performance profiling report., Measures processing duration of compiler phases, planner scheduling latencies,, Verify profiler records durations and computes cache hits/misses rate., test_performance_profiler()

### Community 20 - "runtime/__init__.py"
Cohesion: 0.12
Nodes (13): CancellationToken, Requests cancellation., Returns True if cancellation has been requested., Raises asyncio.CancelledError if cancellation was requested., Blocks asynchronously until cancellation is requested., Cooperative cancellation token to propagate cancellation requests across runtime, NodeExecutionError, PermanentNodeError (+5 more)

### Community 21 - "devtools/__init__.py"
Cohesion: 0.17
Nodes (10): CompilerDiagnostic, ObservabilityDiagnostics, BaseModel, Registry for gathering and querying devtools compiler warnings and issues., Structured warning/diagnostic log generated during compilation stages., DebuggerException, DevToolsError, ValueError (+2 more)

### Community 22 - "ExecutionRecord"
Cohesion: 0.21
Nodes (9): ExecutionRecord, BaseModel, Represents historical execution log results saved in procedural memory., Deletes a CachedPlan from the store by its ID., Saves an ExecutionRecord log entry., Lists all ExecutionRecords saved in the store., Deletes all plans and records from the store., Abstract interface for Procedural Memory pluggable storage engines. (+1 more)

### Community 23 - "api.py"
Cohesion: 0.09
Nodes (21): main(), compile_topology(), get_execution_status(), get_metrics(), get_or_create_cluster(), get_profiler(), get_status(), get_traces() (+13 more)

### Community 24 - "compilerOptions"
Cohesion: 0.08
Nodes (23): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection (+15 more)

### Community 25 - "NodeRegistry"
Cohesion: 0.20
Nodes (7): Submits compiled execution tasks to designated worker queues via the MessageBus,, TaskDispatcher, Checks if a worker has enough free resources., Allocates resources on a worker node and increments its task count., Releases allocated resources on a worker node and decrements its task count., Manages resource allocations, capacity validations, and task counts across clust, ResourceManager

### Community 26 - "test_memory.py"
Cohesion: 0.22
Nodes (5): Generates parallel execution stages.         All nodes in a stage can run in par, Exports the graph to Graphviz DOT format for visualization., Returns True if the execution graph contains directed cycles., Returns a topological sorting of the node IDs., Calculates the critical path of the DAG (the path of node IDs with the maximum

### Community 27 - "RuntimeState"
Cohesion: 0.25
Nodes (4): Removes a node and all of its associated edges from the graph., Checks if a node ID exists in the graph., Returns the immediate successors (consumers) of the given node ID., Returns the immediate predecessors (producers) of the given node ID.

### Community 28 - "IntentParser"
Cohesion: 0.28
Nodes (12): ArgumentParser, build_parser(), compile_cmd(), dashboard_cmd(), debug_cmd(), graph_cmd(), main(), optimize_cmd() (+4 more)

### Community 29 - "LocalMessageBus"
Cohesion: 0.06
Nodes (23): ClusterCoordinator, Subscribes to cluster registrations/unregistrations and coordinates registry ent, Subscribes to registration channels., Unsubscribes from registration channels., Updates worker in registry upon receipt of registration message., Removes worker entry from registry upon worker shutdown., LocalMessageBus, Any (+15 more)

### Community 30 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+11 more)

### Community 31 - "DistributedScheduler"
Cohesion: 0.20
Nodes (11): create_execution_dag(), Verify visualizers generate correct Mermaid flowchart tree formatting., Verify KnowledgeGraphVisualizer renders Graphify Mermaid and computes token savi, Verify devtools CLI parser handles compile, run, status, and debug inputs., Verify dashboard web console endpoints return valid status payloads., Verify tracer opens/closes spans and exports JSON list formats., test_ast_and_dag_visualizers(), test_cli_args_parsing() (+3 more)

### Community 32 - "ReportGenerator"
Cohesion: 0.16
Nodes (12): main(), Any, Compares results of Run A (e.g. Baseline) against Run B (e.g. Optimized)., Any, Generates a Markdown comparative report table., Generates raw JSON report output., Generates a flat CSV report string., Generates a clean HTML report table. (+4 more)

### Community 33 - "RuntimeMetricsTracker"
Cohesion: 0.11
Nodes (10): Any, Starts timing the overall runtime execution., Stops timing the overall runtime execution., Records node startup, updating execution order and parallelism tracking., Records node completion and calculates its duration., Collects and computes performance and run statistics for adaptive executions., Updates parallelism tracking if a node fails or is cancelled., Increments the global retry counter. (+2 more)

### Community 34 - "test_research.py"
Cohesion: 0.33
Nodes (5): Any, Inspects TaskIR structure and outputs descriptive metadata., Inspects optimized Execution DAG structures., Utility to inspect intermediate compiler structures (AST, IR, Symbol Table), StateInspector

### Community 35 - "test_devtools.py"
Cohesion: 0.17
Nodes (12): compile_sandbox(), execute_query(), Compiles the query and runs task execution on a background thread/task., Compiles a natural language query, counts tokens, and estimates optimization sav, run_pipeline_execution(), Any, Recursively traverses AST node structure to build a Mermaid flowchart string., Translates Execution DAG nodes and input-to-output links into Mermaid TD graphs. (+4 more)

### Community 36 - "RelationshipEngine"
Cohesion: 0.13
Nodes (14): BasePass, Base class for all compiler passes., Compiler symbol table to track variables, data flow, and dependency resolution., Inserts a new symbol or updates an existing one., Represents a symbol (e.g. data reference, parameter, node name) in the symbol ta, Looks up a symbol by name., Registers a node ID that consumes the given symbol., Returns all symbols registered in the table. (+6 more)

### Community 38 - "PluginRegistry"
Cohesion: 0.17
Nodes (13): CompilationContext, Holds the state of the compiler throughout the compilation passes., CapabilityConstraintPass, ClassifierPass, IRLoweringPass, Pass 1: Walks the AST, registers execution nodes, assigns unique IDs,     and po, Pass 2: Semantic Intent and Domain Classification., Pass 3: Resolves required capabilities and collects constraints across the compi (+5 more)

### Community 39 - "RuntimeContext"
Cohesion: 0.15
Nodes (12): Event, EventBus, Any, BaseModel, Asynchronous event bus supporting subscription callbacks and event emission., Subscribes a listener callback to the specified event type., Removes a listener callback from subscriptions., Emits an event asynchronously to all subscribed listeners.         Resilient aga (+4 more)

### Community 40 - "Tracer"
Cohesion: 0.29
Nodes (5): Any, BaseModel, Starts tracking a new execution span., Ends an active span, calculating duration and status., TraceSpan

### Community 41 - "SQLiteStore"
Cohesion: 0.22
Nodes (4): Connection, Closes the persistent database connection., SQLite-backed implementation of StorageInterface.     Stores index keys in query, SQLiteStore

### Community 42 - "HeartbeatMonitor"
Cohesion: 0.11
Nodes (13): create_demo_dag(), main(), DistributedClusterManager, Any, Returns cluster resource utilizations and latencies., Unified Orchestrator and entry point for distributed Execution DAG scheduling., Starts background cluster loops and monitors., Stops background cluster loops and monitors. (+5 more)

### Community 43 - "PlanLRUCache"
Cohesion: 0.09
Nodes (16): EmptyCache, PlanLRUCache, Any, Retrieves a plan from the cache. Updates LRU order on hit., Saves a plan in the cache. Evicts LRU item if capacity is exceeded., Removes a plan from the cache., Clears the cache and resets stats., Returns cache metric statistics. (+8 more)

### Community 44 - "JSONStore"
Cohesion: 0.29
Nodes (3): JSONStore, Any, Flat JSON-file-backed implementation of StorageInterface.     Useful for local c

### Community 45 - "ClusterCoordinator"
Cohesion: 0.12
Nodes (16): 1.1 Provider Agnosticism & Adapter Bindings, 1.2 Circular Import Prevention, 1.3 Concurrency & Thread Safety, 1.4 Observability & UI Isolation, 1. Core Architectural Constraints & Rules, 2. Persistence Database Schemas (SQLite), 3. Module Architecture Summary, 4.1 Adding New Capabilities (+8 more)

### Community 46 - "CompilerDebugger"
Cohesion: 0.50
Nodes (3): builds, routes, version

### Community 47 - "BenchmarkRunner"
Cohesion: 0.11
Nodes (10): PassManager, Compiler-style pipeline manager for optimization passes.     Manages pass regist, Registers a pass instance with a unique name., Appends a registered pass name to the active pipeline execution order., Sets or reconfigures the sequence of passes in the pipeline., Enables a pass if it was previously disabled., Disables a pass from execution without removing it from the pipeline., Runs the active pipeline passes in order.         If a pass produces fatal error (+2 more)

### Community 48 - ".run_experiment"
Cohesion: 0.17
Nodes (9): Any, Runs experiment: generates workload, executes benchmarks, and computes stats., Calculates statistical summary for a list of runs., Generates a sequential chain of nodes: n0 -> n1 -> n2..., Generates independent nodes that can execute concurrently., Verify programmatic workload chain and parallel node configurations., Verify mathematical means, medians, standard errors, and percentiles., test_statistical_calculations() (+1 more)

### Community 49 - "PlanRepository"
Cohesion: 0.26
Nodes (4): Raised when storage operations fail., StorageError, PlanRepository, Repository abstraction isolating the storage backend from procedural memory logi

### Community 50 - "MemoryMetricsTracker"
Cohesion: 0.17
Nodes (6): MemoryMetricsTracker, Any, Records the time taken to query/retrieve plans., Increments the reuse counter and adds compilation time savings., Returns the summary dictionary of memory performance metrics., Tracks cache retrieval speed, reuse metrics, and compiler speedups.

### Community 51 - "FaultToleranceManager"
Cohesion: 0.27
Nodes (5): FaultToleranceManager, Any, Scans outstanding dispatches on failed_worker_id and reschedules them on alterna, Helper to find another worker and dispatch task again., Tracks in-flight task dispatches and implements failure recovery redistribution

### Community 52 - ".has_cycle"
Cohesion: 0.12
Nodes (15): 1. Prerequisites, 1. Vercel 1-Click Serverless Deployment, 2. Environment Setup, 2. Multi-Stage Docker Container Deployment, 3. Run Verification Tests, CLI Usage, Cloud Deployment Guide, Codebase Directory Structure (+7 more)

### Community 53 - "api_example.py"
Cohesion: 0.12
Nodes (23): parse_prompt(), ParseRequest, ParseResponse, BaseModel, Serves the compiler frontend HTML page., Compiles a natural language request into TaskIR and ExecutionDAG., serve_frontend(), main() (+15 more)

### Community 54 - ".has_node"
Cohesion: 0.14
Nodes (14): load_checkpoint(), Deserializes and restores a RuntimeState from a file path., Serializes the current RuntimeState and saves it to a file path., save_checkpoint(), CheckpointError, Raised when serialization or deserialization of execution state fails., BaseModel, Maintains the dynamic runtime progress, including completed task variables, (+6 more)

### Community 55 - ".visualize"
Cohesion: 0.31
Nodes (8): ComparisonEngine, Compares two benchmark execution runs to identify latency speedups     and optim, ExperimentManager, Coordinates execution of workloads across multiple runs, aggregating     timings, Computes statistical indicators for benchmark metrics:     Mean, Median, Standar, StatisticalAnalyst, Utility to programmatically construct synthetic workload DAGs     for benchmarki, WorkloadGenerator

### Community 56 - "GraphDiagnostic"
Cohesion: 0.17
Nodes (5): PluginRegistry, Any, Extensible plugin manager allowing registration of custom optimization passes,, Verify modular plugin registrations are independent of core models., test_plugin_registry()

### Community 57 - "DevToolsError"
Cohesion: 0.29
Nodes (10): BaseModel, SandboxRequest, TopologyNode, TopologyRequest, ASTVisualizer, Renders compiler AST tree nodes as Mermaid syntax flowcharts., DAGVisualizer, Renders optimized compiler Execution DAG steps as Mermaid dependency flowcharts. (+2 more)

### Community 58 - ".get_parallel_groups"
Cohesion: 0.50
Nodes (3): Expanding the Oxlint configuration, React Compiler, React + TypeScript + Vite

### Community 59 - "ExperimentError"
Cohesion: 0.15
Nodes (8): CompilerDebugger, Any, Sets a breakpoint at a specific compiler phase., Removes a breakpoint at a specific compiler phase., Triggered by the compiler after completing a phase.         If a breakpoint is s, Compiler debugger allowing step-through breakpoints after compiler phases     (p, Verify debugger triggers registered handler callbacks on breakpoint hits., test_compiler_debugger_breakpoints()

### Community 63 - "KnowledgeManager"
Cohesion: 0.07
Nodes (19): ContextEngine, Any, DiGraph, Pulls a neighborhood subgraph of diameter 'depth' around focus_nodes.         Re, Extracts relevant context subgraphs (focused neighborhoods) from the global Know, KnowledgeManager, Any, High-level orchestration API manager for the Knowledge Graph and Context Engine. (+11 more)

### Community 65 - "CapabilityProfile"
Cohesion: 0.67
Nodes (3): CapabilityProfile, BaseModel, Typical resource requirements and latency baseline profiles for a Capability.

### Community 66 - "BenchmarkRunner"
Cohesion: 0.21
Nodes (9): BenchmarkRunner, Executes compilation passes and task pipelines multiple times     to gather repr, Runs compilation and execution workloads repeatedly in an async context,, Synchronous wrapper for run_workload_async., ExperimentConfig, BaseModel, Pydantic parameters defining compiler configuration, scheduling policies,     ru, Verify runner runs iterations and outputs averages metrics. (+1 more)

### Community 70 - "SQLiteGraphStore"
Cohesion: 0.15
Nodes (4): SQLite-backed graph persistence store., SQLiteGraphStore, Verify persisting and loading nodes and relationships in SQLite/JSON., test_sqlite_and_json_graph_stores()

### Community 71 - "OntologyEntity"
Cohesion: 0.25
Nodes (3): ClusterMetricsTracker, Any, Tracks worker utilization, task throughput, execution latency, and schedule coun

### Community 72 - "ContextEngine"
Cohesion: 0.29
Nodes (4): EntityResolver, DiGraph, Resolves pronouns in query using recency and semantic verb matching., Resolves pronoun references (e.g. 'it', 'them', 'the report') to concrete entiti

### Community 73 - "ExperimentError"
Cohesion: 0.50
Nodes (3): ExperimentError, ValueError, Base exception for all research and experimentation errors.

### Community 75 - "PassManager"
Cohesion: 0.25
Nodes (4): PassManager, Manages registration and execution of compiler passes., Registers a compiler pass., Executes all registered passes sequentially.

## Knowledge Gaps
- **103 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+98 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Capability` connect `Capability` to `passes.py`, `test_planner.py`, `DistributedClusterManager`, `OptimizedExecutionDAG`, `test_knowledge.py`, `AdaptiveRuntime`, `Diagnostic`, `ClusterWorker`, `graph_manager.py`, `cluster_manager.py`, `KnowledgeGraph`, `CachedPlan`, `api.py`, `LocalMessageBus`, `DistributedScheduler`, `RelationshipEngine`, `PluginRegistry`, `HeartbeatMonitor`, `api_example.py`, `.visualize`, `DevToolsError`, `.execute`, `KnowledgeManager`, `CapabilityProfile`?**
  _High betweenness centrality (0.263) - this node is a cross-community bridge._
- **Why does `OptimizedExecutionDAG` connect `OptimizedExecutionDAG` to `test_planner.py`, `Capability`, `DistributedClusterManager`, `ExecutionGraph`, `AdaptiveRuntime`, `Diagnostic`, `RuntimeNodeStatus`, `ProceduralMemory`, `cluster_manager.py`, `CachedPlan`, `ExecutionRecord`, `DistributedScheduler`, `test_research.py`, `test_devtools.py`, `HeartbeatMonitor`, `PlanLRUCache`, `.run_experiment`, `.visualize`, `DevToolsError`, `BenchmarkRunner`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Why does `TaskIR` connect `Capability` to `passes.py`, `test_planner.py`, `test_research.py`, `test_devtools.py`, `RelationshipEngine`, `OptimizedExecutionDAG`, `PluginRegistry`, `AdaptiveRuntime`, `Diagnostic`, `PlanLRUCache`, `ProceduralMemory`, `cluster_manager.py`, `CachedPlan`, `api_example.py`, `ExecutionRecord`, `DevToolsError`, `DistributedScheduler`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Are the 59 inferred relationships involving `Capability` (e.g. with `BrokenWorker` and `ClusterWorker`) actually correct?**
  _`Capability` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 48 inferred relationships involving `TaskIR` (e.g. with `ParseRequest` and `ParseResponse`) actually correct?**
  _`TaskIR` has 48 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `OptimizedExecutionDAG` (e.g. with `StateInspector` and `DistributedClusterManager`) actually correct?**
  _`OptimizedExecutionDAG` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 33 inferred relationships involving `Dependency` (e.g. with `CapabilityConstraintPass` and `ClassifierPass`) actually correct?**
  _`Dependency` has 33 INFERRED edges - model-reasoned connections that need verification._