import os
import pytest
import asyncio
import tempfile
from typing import Dict, Any
from omnicore.ir.enums import Capability
from omnicore.ir.models import TaskIR, Dependency
from omnicore.optimizer.optimization_context import OptimizedExecutionNode, OptimizedExecutionDAG
from omnicore.execution.execution_node import RuntimeNodeStatus
from omnicore.runtime.runtime import AdaptiveRuntime
from omnicore.runtime.event_bus import Event
from omnicore.runtime.retry_policy import RetryPolicy
from omnicore.runtime.adapters.capability_adapter import MockCapabilityAdapter, CapabilityAdapter
from omnicore.runtime.exceptions import NodeExecutionError, PermanentNodeError

# --- Test Helpers ---

def create_simple_dag() -> OptimizedExecutionDAG:
    """
    Creates a simple DAG:
    search_1 -> compare_1 -> summarize_1
    """
    node1 = OptimizedExecutionNode(
        node_id="search_1",
        name="Search Node",
        description="Search info",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings",
        estimated_time=1.0,
        parallelizable=True
    )
    node2 = OptimizedExecutionNode(
        node_id="compare_1",
        name="Compare Node",
        description="Compare findings",
        capability=Capability.COMPARISON,
        input="findings",
        output="comparison",
        estimated_time=1.0,
        parallelizable=True
    )
    node3 = OptimizedExecutionNode(
        node_id="summarize_1",
        name="Summarize Node",
        description="Summarize results",
        capability=Capability.SUMMARIZATION,
        input="comparison",
        output="summary",
        estimated_time=1.0,
        parallelizable=True
    )
    
    return OptimizedExecutionDAG(
        nodes=[node1, node2, node3],
        dependencies=[
            Dependency(source="search_1", target="compare_1"),
            Dependency(source="compare_1", target="summarize_1")
        ],
        topological_order=["search_1", "compare_1", "summarize_1"],
        stages=[["search_1"], ["compare_1"], ["summarize_1"]],
        critical_path=["search_1", "compare_1", "summarize_1"]
    )

def create_parallel_dag() -> OptimizedExecutionDAG:
    """
    Creates a parallel branch DAG:
    search_1 \
             -> compare_1 -> summarize_1
    search_2 /
    """
    node1 = OptimizedExecutionNode(
        node_id="search_1",
        name="Search Github",
        description="Search Github repo",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings1",
        estimated_time=1.0,
        parallelizable=True
    )
    node2 = OptimizedExecutionNode(
        node_id="search_2",
        name="Search Docs",
        description="Search documentation",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings2",
        estimated_time=1.0,
        parallelizable=True
    )
    node3 = OptimizedExecutionNode(
        node_id="compare_1",
        name="Compare",
        description="Compare search findings",
        capability=Capability.COMPARISON,
        input=["findings1", "findings2"],
        output="comparison",
        estimated_time=1.0,
        parallelizable=True
    )
    node4 = OptimizedExecutionNode(
        node_id="summarize_1",
        name="Summarize",
        description="Summarize comparison",
        capability=Capability.SUMMARIZATION,
        input="comparison",
        output="summary",
        estimated_time=1.0,
        parallelizable=True
    )

    return OptimizedExecutionDAG(
        nodes=[node1, node2, node3, node4],
        dependencies=[
            Dependency(source="search_1", target="compare_1"),
            Dependency(source="search_2", target="compare_1"),
            Dependency(source="compare_1", target="summarize_1")
        ],
        topological_order=["search_1", "search_2", "compare_1", "summarize_1"],
        stages=[["search_1", "search_2"], ["compare_1"], ["summarize_1"]],
        critical_path=["search_1", "compare_1", "summarize_1"]
    )

# --- Unit Tests ---

@pytest.mark.asyncio
async def test_scheduler_sequential_execution():
    """Verify that nodes run sequentially respecting dependencies."""
    dag = create_simple_dag()
    adapter = MockCapabilityAdapter(latency=0.01)
    runtime = AdaptiveRuntime(adapter=adapter)
    
    result = await runtime.execute(dag, inputs={"query": "python compiler"})
    
    assert result.status == RuntimeNodeStatus.COMPLETED
    assert "summary" in result.outputs
    assert len(result.node_results) == 3
    
    # Assert execution order matches topological dependency constraints
    order = result.metrics["execution_order"]
    assert order.index("search_1") < order.index("compare_1")
    assert order.index("compare_1") < order.index("summarize_1")


@pytest.mark.asyncio
async def test_parallel_execution_concurrency():
    """Verify that independent nodes run concurrently in parallel."""
    dag = create_parallel_dag()
    # High enough latency to guarantee overlap
    adapter = MockCapabilityAdapter(latency=0.1)
    runtime = AdaptiveRuntime(adapter=adapter)
    
    result = await runtime.execute(dag, inputs={"query": "python servers"})
    
    assert result.status == RuntimeNodeStatus.COMPLETED
    assert result.metrics["peak_parallelism"] >= 2
    
    # Verify outputs are propagated
    assert "findings1" in result.outputs
    assert "findings2" in result.outputs
    assert "summary" in result.outputs


@pytest.mark.asyncio
async def test_event_bus_monitoring():
    """Verify that event bus registers and emits runtime lifecycle events."""
    dag = create_simple_dag()
    adapter = MockCapabilityAdapter(latency=0.01)
    runtime = AdaptiveRuntime(adapter=adapter)
    
    emitted_events = []
    
    def log_event(event: Event):
        emitted_events.append(event.event_type)
        
    runtime.context.event_bus.subscribe("runtime_started", log_event)
    runtime.context.event_bus.subscribe("node_started", log_event)
    runtime.context.event_bus.subscribe("node_completed", log_event)
    runtime.context.event_bus.subscribe("runtime_finished", log_event)
    
    await runtime.execute(dag, inputs={"query": "test"})
    
    assert "runtime_started" in emitted_events
    assert "node_started" in emitted_events
    assert "node_completed" in emitted_events
    assert "runtime_finished" in emitted_events
    assert emitted_events.count("node_completed") == 3


@pytest.mark.asyncio
async def test_retry_policy_transient_failure():
    """Verify that transient failures trigger retries with backoff delay."""
    dag = create_simple_dag()
    
    class FaultyAdapter(CapabilityAdapter):
        def __init__(self):
            self.calls = 0
            
        async def execute(self, capability: Capability, inputs: Dict[str, Any], context: Any) -> Dict[str, Any]:
            self.calls += 1
            if capability == Capability.WEB_SEARCH and self.calls < 3:
                raise ValueError("Temporary connection timeout")
            return {"findings": "success on call 3", "comparison": "comparison", "summary": "summary"}
            
    adapter = FaultyAdapter()
    policy = RetryPolicy(max_retries=4, base_delay=0.01)
    runtime = AdaptiveRuntime(adapter=adapter, retry_policy=policy)
    
    result = await runtime.execute(dag, inputs={"query": "test"})
    
    assert result.status == RuntimeNodeStatus.COMPLETED
    assert result.metrics["total_retries"] == 2
    assert result.node_results["search_1"].retry_count == 2


@pytest.mark.asyncio
async def test_permanent_failure_fast_path():
    """Verify that permanent errors fail fast immediately without retries."""
    dag = create_simple_dag()
    
    class PermanentFailAdapter(CapabilityAdapter):
        async def execute(self, capability: Capability, inputs: Dict[str, Any], context: Any) -> Dict[str, Any]:
            raise PermanentNodeError("search_1", "Invalid API key structure")
            
    adapter = PermanentFailAdapter()
    policy = RetryPolicy(max_retries=5, base_delay=0.01)
    runtime = AdaptiveRuntime(adapter=adapter, retry_policy=policy)
    
    result = await runtime.execute(dag, inputs={"query": "test"})
    
    assert result.status == RuntimeNodeStatus.FAILED
    assert result.metrics["total_retries"] == 0
    assert "Node 'search_1' error" in result.diagnostics[0]


@pytest.mark.asyncio
async def test_cancellation_tokens():
    """Verify that requesting cancellation halts execution gracefully."""
    dag = create_parallel_dag()
    
    class SlowAdapter(CapabilityAdapter):
        async def execute(self, capability: Capability, inputs: Dict[str, Any], context: Any) -> Dict[str, Any]:
            await asyncio.sleep(0.5)
            return {"findings1": "f1", "findings2": "f2"}
            
    adapter = SlowAdapter()
    runtime = AdaptiveRuntime(adapter=adapter)
    
    # Schedule cancellation after 0.1 seconds
    async def cancel_task():
        await asyncio.sleep(0.1)
        runtime.context.cancellation_token.cancel()
        
    asyncio.create_task(cancel_task())
    
    result = await runtime.execute(dag, inputs={"query": "test"})
    
    assert result.status == RuntimeNodeStatus.CANCELLED
    
    # Assert that subsequent/downstream steps were not completed
    assert result.node_results["compare_1"].status == RuntimeNodeStatus.PENDING


@pytest.mark.asyncio
async def test_checkpointing_and_resume():
    """Verify state serialization and resuming failed pipelines from checkpoints."""
    with tempfile.TemporaryDirectory() as tmpdir:
        checkpoint_path = os.path.join(tmpdir, "checkpoint.json")
        dag = create_simple_dag()
        
        # 1. Setup adapter that fails on step 2 (compare_1)
        class IntermittentAdapter(CapabilityAdapter):
            def __init__(self):
                self.should_fail = True
                
            async def execute(self, capability: Capability, inputs: Dict[str, Any], context: Any) -> Dict[str, Any]:
                if capability == Capability.WEB_SEARCH:
                    return {"findings": "search outputs"}
                elif capability == Capability.COMPARISON:
                    if self.should_fail:
                        raise ValueError("Transient engine error")
                    return {"comparison": "comparison outputs"}
                elif capability == Capability.SUMMARIZATION:
                    return {"summary": "final summary output"}
                return {}

        adapter = IntermittentAdapter()
        policy = RetryPolicy(max_retries=1, base_delay=0.01) # No retries to fail fast
        
        # Run first time
        runtime1 = AdaptiveRuntime(adapter=adapter, retry_policy=policy, checkpoint_filepath=checkpoint_path)
        result1 = await runtime1.execute(dag, inputs={"query": "test"})
        
        assert result1.status == RuntimeNodeStatus.FAILED
        assert result1.node_results["search_1"].status == RuntimeNodeStatus.COMPLETED
        assert result1.node_results["compare_1"].status == RuntimeNodeStatus.FAILED
        
        # Checkpoint file should exist
        assert os.path.exists(checkpoint_path)
        
        # 2. Fix the adapter error and resume
        adapter.should_fail = False
        runtime2 = AdaptiveRuntime(adapter=adapter, retry_policy=policy, checkpoint_filepath=checkpoint_path)
        
        # Executing with resume=True
        result2 = await runtime2.execute(dag, inputs={"query": "test"}, resume=True)
        
        assert result2.status == RuntimeNodeStatus.COMPLETED
        # The first step search_1 should be resumed successfully from state
        assert result2.node_results["search_1"].status == RuntimeNodeStatus.COMPLETED
        assert result2.node_results["compare_1"].status == RuntimeNodeStatus.COMPLETED
        assert result2.node_results["summarize_1"].status == RuntimeNodeStatus.COMPLETED
        assert "summary" in result2.outputs
