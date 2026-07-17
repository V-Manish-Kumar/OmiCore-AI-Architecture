import pytest
from omnicore.ir.enums import Capability, TaskIntent, Complexity, NodeStatus
from omnicore.ir.models import TaskIR, ExecutionNode, Dependency, ExecutionDAG
from omnicore.optimizer.optimizer import TaskOptimizer
from omnicore.optimizer.optimization_context import (
    OptimizerState,
    OptimizedExecutionNode,
    OptimizedExecutionDAG,
    Diagnostic,
    DiagnosticSeverity,
    SearchCapability,
    SummarizationCapability,
    ReportGenerationCapability
)
from omnicore.optimizer.exceptions import ValidationError, CycleError
from omnicore.optimizer.pass_manager import PassManager, BaseOptimizerPass
from omnicore.optimizer.passes.validation_pass import ValidationPass
from omnicore.optimizer.passes.capability_resolution_pass import CapabilityResolutionPass
from omnicore.optimizer.passes.dependency_analysis_pass import DependencyAnalysisPass
from omnicore.optimizer.passes.parallelization_pass import ParallelizationPass
from omnicore.optimizer.passes.graph_optimization_pass import GraphOptimizationPass
from omnicore.optimizer.passes.cost_estimation_pass import CostEstimationPass
from omnicore.optimizer.passes.scheduling_pass import SchedulingPass
from omnicore.optimizer.passes.optimization_report_pass import OptimizationReportPass

# --- Setup Helpers ---
def create_basic_task_ir(inputs=None, outputs=None, constraints=None) -> TaskIR:
    return TaskIR(
        task_id="test_task_123",
        primary_intent=TaskIntent.RESEARCH,
        domain="General",
        user_goal="Search and summarize python tips",
        inputs=inputs or ["query"],
        outputs=outputs or ["summary"],
        constraints=constraints or ["Must be brief"]
    )

def create_basic_execution_dag(nodes, dependencies=None) -> ExecutionDAG:
    return ExecutionDAG(
        nodes=nodes,
        dependencies=dependencies or [],
        topological_order=[n.node_id for n in nodes]
    )

# --- Unit Tests ---

def test_pass_manager_configuration():
    """Verify PassManager registration, ordering, and execution stats."""
    class DummyPass(BaseOptimizerPass):
        def run(self, state: OptimizerState) -> OptimizerState:
            return state

    manager = PassManager()
    dummy = DummyPass()
    manager.register_pass("dummy", dummy)
    manager.add_pass_to_pipeline("dummy")
    
    assert "dummy" in manager.get_statistics()["active_pipeline"]
    
    manager.disable_pass("dummy")
    assert "dummy" in manager.get_statistics()["disabled_passes"]
    assert "dummy" not in manager.get_statistics()["active_pipeline"]
    
    manager.enable_pass("dummy")
    assert "dummy" in manager.get_statistics()["active_pipeline"]


def test_validation_pass_duplicate_node_ids():
    """Duplicate node IDs should trigger validation errors."""
    node1 = ExecutionNode(
        node_id="node_1",
        name="Search 1",
        description="Search Github",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="out1"
    )
    node2 = ExecutionNode(
        node_id="node_1",  # Duplicate ID
        name="Search 2",
        description="Search Docs",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="out2"
    )
    
    task_ir = create_basic_task_ir(outputs=["out1", "out2"])
    dag = create_basic_execution_dag([node1, node2])
    
    optimizer = TaskOptimizer()
    with pytest.raises(ValidationError) as excinfo:
        optimizer.optimize(task_ir, dag)
    
    assert "Duplicate node ID detected" in str(excinfo.value)


def test_validation_pass_invalid_dependency():
    """Dependencies pointing to invalid node IDs should raise a ValidationError."""
    node = ExecutionNode(
        node_id="node_1",
        name="Search",
        description="Search stuff",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="out"
    )
    
    task_ir = create_basic_task_ir(outputs=["out"])
    dag = create_basic_execution_dag(
        nodes=[node],
        dependencies=[Dependency(source="node_1", target="invalid_node")]
    )
    
    optimizer = TaskOptimizer()
    with pytest.raises(ValidationError) as excinfo:
        optimizer.optimize(task_ir, dag)
        
    assert "refers to a non-existent node" in str(excinfo.value)


def test_validation_pass_missing_inputs():
    """Consuming an input that does not exist globally or from a predecessor should error."""
    node = ExecutionNode(
        node_id="node_1",
        name="Summarize",
        description="Summarize query results",
        capability=Capability.SUMMARIZATION,
        input=["missing_input_symbol"],  # Not globally defined, not produced by any node
        output="summary"
    )
    
    task_ir = create_basic_task_ir(inputs=["query"], outputs=["summary"])
    dag = create_basic_execution_dag([node])
    
    optimizer = TaskOptimizer()
    with pytest.raises(ValidationError) as excinfo:
        optimizer.optimize(task_ir, dag)
        
    assert "consumes input 'missing_input_symbol' which is not produced" in str(excinfo.value)


def test_validation_pass_missing_outputs():
    """If a required global output is never produced, validation should fail."""
    node = ExecutionNode(
        node_id="node_1",
        name="Search",
        description="Search query",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings"
    )
    
    task_ir = create_basic_task_ir(inputs=["query"], outputs=["summary"])  # summary is expected, findings is produced
    dag = create_basic_execution_dag([node])
    
    optimizer = TaskOptimizer()
    with pytest.raises(ValidationError) as excinfo:
        optimizer.optimize(task_ir, dag)
        
    assert "Global output 'summary' is required but not produced" in str(excinfo.value)


def test_validation_pass_cycle_detection():
    """Cyclic dependency structures must trigger a validation error."""
    node1 = ExecutionNode(
        node_id="node_1",
        name="Search",
        description="Search query",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings"
    )
    node2 = ExecutionNode(
        node_id="node_2",
        name="Compare",
        description="Compare findings",
        capability=Capability.COMPARISON,
        input="findings",
        output="comparison"
    )
    
    task_ir = create_basic_task_ir(outputs=["comparison"])
    dag = create_basic_execution_dag(
        nodes=[node1, node2],
        dependencies=[
            Dependency(source="node_1", target="node_2"),
            Dependency(source="node_2", target="node_1")  # Cycle!
        ]
    )
    
    optimizer = TaskOptimizer()
    with pytest.raises(ValidationError) as excinfo:
        optimizer.optimize(task_ir, dag)
        
    assert "Dependency cycle detected" in str(excinfo.value)


def test_capability_resolution_pass():
    """Ensure abstract capabilities map correctly to descriptors."""
    node1 = ExecutionNode(
        node_id="node_1",
        name="Search Node",
        description="Search info",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings"
    )
    
    task_ir = create_basic_task_ir(outputs=["findings"])
    dag = create_basic_execution_dag([node1])
    
    # We run manually to inspect intermediate states
    initial_dag = OptimizedExecutionDAG(
        nodes=[OptimizedExecutionNode(**node1.model_dump())],
        dependencies=dag.dependencies,
        topological_order=dag.topological_order
    )
    state = OptimizerState(task_ir=task_ir, execution_dag=initial_dag)
    
    pass_inst = CapabilityResolutionPass()
    new_state = pass_inst.run(state)
    
    resolved_node = new_state.execution_dag.nodes[0]
    assert resolved_node.resolved_capability is not None
    assert isinstance(resolved_node.resolved_capability, SearchCapability)


def test_dependency_analysis_pass():
    """Verify that implicit dataflow dependencies are successfully constructed."""
    node1 = ExecutionNode(
        node_id="node_1",
        name="Search",
        description="Search info",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings"
    )
    node2 = ExecutionNode(
        node_id="node_2",
        name="Summarize",
        description="Summarize findings",
        capability=Capability.SUMMARIZATION,
        input="findings",  # Consumes findings from node_1
        output="summary"
    )
    
    task_ir = create_basic_task_ir(outputs=["summary"])
    dag = create_basic_execution_dag([node1, node2], dependencies=[]) # No explicit dependencies provided
    
    initial_dag = OptimizedExecutionDAG(
        nodes=[OptimizedExecutionNode(**n.model_dump()) for n in dag.nodes],
        dependencies=dag.dependencies,
        topological_order=dag.topological_order
    )
    state = OptimizerState(task_ir=task_ir, execution_dag=initial_dag)
    
    # Run CapabilityResolution then DependencyAnalysis
    state = CapabilityResolutionPass().run(state)
    new_state = DependencyAnalysisPass().run(state)
    
    # Verify that a dependency edge node_1 -> node_2 was automatically constructed
    deps = [d.to_tuple() for d in new_state.execution_dag.dependencies]
    assert ("node_1", "node_2") in deps


def test_parallelization_pass():
    """Verify parallelizable nodes and stages are correctly analyzed."""
    node1 = ExecutionNode(
        node_id="node_1",
        name="Search 1",
        description="Search Github",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings1"
    )
    node2 = ExecutionNode(
        node_id="node_2",
        name="Search 2",
        description="Search Docs",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings2"
    )
    node3 = ExecutionNode(
        node_id="node_3",
        name="PDF Generator",
        description="Compile to PDF",
        capability=Capability.PDF_GENERATION,  # Inherently sequential/non-parallelizable
        input=["findings1", "findings2"],
        output="pdf"
    )
    
    task_ir = create_basic_task_ir(outputs=["pdf"])
    dag = create_basic_execution_dag(
        nodes=[node1, node2, node3],
        dependencies=[
            Dependency(source="node_1", target="node_3"),
            Dependency(source="node_2", target="node_3")
        ]
    )
    
    initial_dag = OptimizedExecutionDAG(
        nodes=[OptimizedExecutionNode(**n.model_dump()) for n in dag.nodes],
        dependencies=dag.dependencies,
        topological_order=dag.topological_order
    )
    state = OptimizerState(task_ir=task_ir, execution_dag=initial_dag)
    
    state = CapabilityResolutionPass().run(state)
    state = DependencyAnalysisPass().run(state)
    new_state = ParallelizationPass().run(state)
    
    node_lookup = {n.node_id: n for n in new_state.execution_dag.nodes}
    assert node_lookup["node_1"].parallelizable is True
    assert node_lookup["node_2"].parallelizable is True
    assert node_lookup["node_3"].parallelizable is False  # Forced sequential by capability rules
    
    # We should have a parallel group ID for node_1 and node_2 because they can run in parallel in stage 0
    assert node_lookup["node_1"].parallel_group_id is not None
    assert node_lookup["node_1"].parallel_group_id == node_lookup["node_2"].parallel_group_id


def test_graph_optimization_duplicate_elimination():
    """Duplicate/redundant nodes should be merged and downstream inputs rewritten."""
    node1 = ExecutionNode(
        node_id="node_1",
        name="Search 1",
        description="Search query",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="out1"
    )
    node2 = ExecutionNode(
        node_id="node_2",  # Duplicate: same capability, same input, not a side-effect node
        name="Search 2",
        description="Search query duplicates",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="out2"
    )
    node3 = ExecutionNode(
        node_id="node_3",
        name="Summarize",
        description="Summarize output 2",
        capability=Capability.SUMMARIZATION,
        input="out2",  # Consumes the output of the duplicate node
        output="summary"
    )
    
    task_ir = create_basic_task_ir(outputs=["summary"])
    dag = create_basic_execution_dag(
        nodes=[node1, node2, node3],
        dependencies=[Dependency(source="node_2", target="node_3")]
    )
    
    initial_dag = OptimizedExecutionDAG(
        nodes=[OptimizedExecutionNode(**n.model_dump()) for n in dag.nodes],
        dependencies=dag.dependencies,
        topological_order=dag.topological_order
    )
    state = OptimizerState(task_ir=task_ir, execution_dag=initial_dag)
    
    state = CapabilityResolutionPass().run(state)
    state = DependencyAnalysisPass().run(state)
    new_state = GraphOptimizationPass().run(state)
    
    opt_nodes = new_state.execution_dag.nodes
    opt_node_ids = [n.node_id for n in opt_nodes]
    
    # node_2 should have been eliminated as a duplicate
    assert "node_1" in opt_node_ids
    assert "node_2" not in opt_node_ids
    assert "node_3" in opt_node_ids
    
    # node_3's input should have been rewritten to "out1" (output of node_1)
    node3_opt = next(n for n in opt_nodes if n.node_id == "node_3")
    assert "out1" in node3_opt.input
    assert "out2" not in node3_opt.input
    
    # The dependency edge should now point from node_1 to node_3
    deps = [d.to_tuple() for d in new_state.execution_dag.dependencies]
    assert ("node_1", "node_3") in deps


def test_graph_optimization_dead_node_elimination():
    """Unused/dead nodes that do not contribute to final outputs or have side effects should be pruned."""
    node1 = ExecutionNode(
        node_id="node_1",
        name="Search Useful",
        description="Search query",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="out1"
    )
    node2 = ExecutionNode(
        node_id="node_2",  # Dead: output is never consumed, and not in task_ir outputs
        name="Search Dead",
        description="Search unused query",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="unused_out"
    )
    node3 = ExecutionNode(
        node_id="node_3",
        name="Summarize",
        description="Summarize output 1",
        capability=Capability.SUMMARIZATION,
        input="out1",
        output="summary"
    )
    
    task_ir = create_basic_task_ir(outputs=["summary"])
    dag = create_basic_execution_dag([node1, node2, node3])
    
    initial_dag = OptimizedExecutionDAG(
        nodes=[OptimizedExecutionNode(**n.model_dump()) for n in dag.nodes],
        dependencies=dag.dependencies,
        topological_order=dag.topological_order
    )
    state = OptimizerState(task_ir=task_ir, execution_dag=initial_dag)
    
    state = CapabilityResolutionPass().run(state)
    state = DependencyAnalysisPass().run(state)
    new_state = GraphOptimizationPass().run(state)
    
    opt_nodes = new_state.execution_dag.nodes
    opt_node_ids = [n.node_id for n in opt_nodes]
    
    assert "node_1" in opt_node_ids
    assert "node_3" in opt_node_ids
    assert "node_2" not in opt_node_ids  # Pruned


def test_graph_optimization_dead_node_cascading():
    """Pruning a dead node should cascades up and prune predecessor nodes if they become dead too."""
    node1 = ExecutionNode(
        node_id="node_1",
        name="Search Predecessor",
        description="Search query",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="out1"
    )
    node2 = ExecutionNode(
        node_id="node_2",
        name="Summarize Predecessor",
        description="Summarize output",
        capability=Capability.SUMMARIZATION,
        input="out1",
        output="out2"
    )
    node3 = ExecutionNode(
        node_id="node_3",  # Real worker node producing final output
        name="Report Creator",
        description="Create report",
        capability=Capability.REPORT_GENERATION,  # Has side effects, should never be pruned
        input="query",
        output="report"
    )
    
    task_ir = create_basic_task_ir(outputs=["report"])
    dag = create_basic_execution_dag(
        nodes=[node1, node2, node3],
        dependencies=[Dependency(source="node_1", target="node_2")]
    )
    
    initial_dag = OptimizedExecutionDAG(
        nodes=[OptimizedExecutionNode(**n.model_dump()) for n in dag.nodes],
        dependencies=dag.dependencies,
        topological_order=dag.topological_order
    )
    state = OptimizerState(task_ir=task_ir, execution_dag=initial_dag)
    
    state = CapabilityResolutionPass().run(state)
    state = DependencyAnalysisPass().run(state)
    new_state = GraphOptimizationPass().run(state)
    
    opt_nodes = new_state.execution_dag.nodes
    opt_node_ids = [n.node_id for n in opt_nodes]
    
    # Since out2 is not consumed and not a global output, node2 is dead.
    # When node2 is removed, its input 'out1' is no longer consumed, so node1 becomes dead and is also removed.
    # node3 has a side effect and produces the required output 'report', so it is preserved.
    assert "node_3" in opt_node_ids
    assert "node_2" not in opt_node_ids
    assert "node_1" not in opt_node_ids


# --- Integration/End-to-End Tests ---

def test_end_to_end_optimization_pipeline():
    """Ensure the complete optimizer pipeline executes successfully and returns an optimized DAG."""
    # 1. Construct initial compilation output from Module 1
    node1 = ExecutionNode(
        node_id="search_1",
        name="Search Node",
        description="Search Github",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings1"
    )
    node2 = ExecutionNode(
        node_id="search_2",  # Duplicate search
        name="Search Node 2",
        description="Search Github",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings2"
    )
    node3 = ExecutionNode(
        node_id="summarize_1",
        name="Summarize Node",
        description="Summarize search results",
        capability=Capability.SUMMARIZATION,
        input=["findings1", "findings2"],
        output="summary"
    )
    node4 = ExecutionNode(
        node_id="pdf_1",
        name="PDF Node",
        description="Generate PDF",
        capability=Capability.PDF_GENERATION,
        input="summary",
        output="pdf"
    )
    node5 = ExecutionNode(
        node_id="unused_1",  # Dead node
        name="Unused Search",
        description="Unused query",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="unused_out"
    )
    
    task_ir = create_basic_task_ir(inputs=["query"], outputs=["pdf"])
    
    dag = create_basic_execution_dag(
        nodes=[node1, node2, node3, node4, node5],
        dependencies=[
            Dependency(source="search_1", target="summarize_1"),
            Dependency(source="search_2", target="summarize_1"),
            Dependency(source="summarize_1", target="pdf_1")
        ]
    )
    
    # 2. Run optimizer
    optimizer = TaskOptimizer()
    opt_dag, report = optimizer.optimize(task_ir, dag)
    
    # 3. Assert report details
    assert "search_1" in report.original_nodes
    assert "search_2" in report.original_nodes
    assert "pdf_1" in report.original_nodes
    assert "unused_1" in report.original_nodes
    
    assert "unused_1" in report.removed_nodes
    assert "search_2" in report.removed_nodes or "search_2" in report.merged_nodes
    
    assert report.estimated_runtime > 0.0
    assert report.estimated_cost > 0.0
    assert report.estimated_tokens > 0
    assert len(report.optimization_passes_applied) == 8
    
    # 4. Assert optimized DAG details
    opt_node_ids = [n.node_id for n in opt_dag.nodes]
    assert "unused_1" not in opt_node_ids
    assert "search_2" not in opt_node_ids
    assert "search_1" in opt_node_ids
    assert "summarize_1" in opt_node_ids
    assert "pdf_1" in opt_node_ids
    
    # Ensure stages are set
    assert len(opt_dag.stages) > 0
    
    # Ensure critical path is set
    assert len(opt_dag.critical_path) > 0
    assert opt_dag.critical_path[0] == "search_1"
    assert opt_dag.critical_path[-1] == "pdf_1"
