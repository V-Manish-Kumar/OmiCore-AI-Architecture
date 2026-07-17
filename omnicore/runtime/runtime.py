import os
import asyncio
from typing import Dict, Any, Optional, Tuple
from omnicore.optimizer.optimization_context import OptimizedExecutionDAG
from omnicore.execution.execution_plan import ExecutionPlan
from omnicore.execution.execution_node import RuntimeNodeStatus, ExecutionNodeState
from omnicore.execution.execution_result import ExecutionResult
from omnicore.runtime.runtime_state import RuntimeState
from omnicore.runtime.runtime_context import RuntimeContext
from omnicore.runtime.adapters.capability_adapter import CapabilityAdapter
from omnicore.runtime.event_bus import EventBus
from omnicore.runtime.retry_policy import RetryPolicy
from omnicore.runtime.executor import RuntimeExecutor
from omnicore.runtime.checkpoint import load_checkpoint

class AdaptiveRuntime:
    """
    Main entry point for executing optimized task execution plans.
    Orchestrates the scheduler, concurrency executor, event emissions, and metrics collection.
    """
    def __init__(
        self,
        adapter: CapabilityAdapter,
        retry_policy: Optional[RetryPolicy] = None,
        event_bus: Optional[EventBus] = None,
        checkpoint_filepath: Optional[str] = None
    ):
        self.context = RuntimeContext(
            adapter=adapter,
            retry_policy=retry_policy or RetryPolicy(),
            event_bus=event_bus or EventBus(),
            checkpoint_filepath=checkpoint_filepath
        )

    async def execute(
        self,
        dag: OptimizedExecutionDAG,
        inputs: Optional[Dict[str, Any]] = None,
        resume: bool = False
    ) -> ExecutionResult:
        """
        Executes the given optimized Execution DAG.
        If 'resume' is True and a valid checkpoint exists at checkpoint_filepath,
        it resumes execution from that state instead of starting fresh.
        """
        # 1. Initialize Plan
        plan = ExecutionPlan.from_dag(dag)
        
        # 2. Checkpoint restoration/resume or fresh state initialization
        state = None
        if resume and self.context.checkpoint_filepath and os.path.exists(self.context.checkpoint_filepath):
            try:
                state = load_checkpoint(self.context.checkpoint_filepath)
            except Exception:
                # If loading checkpoint fails, fall back to fresh state
                pass

        if state is None:
            # Initialize fresh RuntimeState
            state = RuntimeState(plan_id=plan.plan_id)
            for nid, node in plan.nodes.items():
                state.node_statuses[nid] = RuntimeNodeStatus.PENDING
                state.node_states[nid] = ExecutionNodeState(node=node)
            state.variables = dict(inputs or {})

        # 3. Start timing and execution events
        self.context.metrics_tracker.start_runtime()
        await self.context.event_bus.emit("runtime_started", {"plan_id": plan.plan_id, "node_count": len(plan.nodes)})

        # 4. Trigger the DAG Executor loop
        executor = RuntimeExecutor(plan, self.context)
        try:
            await executor.execute(state)
        except (Exception, asyncio.CancelledError):
            # Catch exceptions to ensure metrics stop and clean report generation
            pass

        # 5. Stop timing and finalize metrics
        self.context.metrics_tracker.finish_runtime()

        # 6. Evaluate execution status
        final_status = RuntimeNodeStatus.COMPLETED
        if self.context.cancellation_token.is_cancelled:
            final_status = RuntimeNodeStatus.CANCELLED
        else:
            # If any active/executed node failed, the plan status is FAILED
            for nid, status in state.node_statuses.items():
                if status == RuntimeNodeStatus.FAILED:
                    final_status = RuntimeNodeStatus.FAILED
                    break

        # 7. Collect output variables
        # Map values matching variables listed in the original DAG's outputs or task goals
        output_keys = set()
        for node in dag.nodes:
            node_outputs = node.output or []
            if isinstance(node_outputs, str):
                node_outputs = [node_outputs]
            for o in node_outputs:
                output_keys.add(o)
                
        final_outputs = {k: state.variables[k] for k in output_keys if k in state.variables}

        # 8. Compile the report and emit completion event
        metrics = self.context.metrics_tracker.get_summary(
            total_nodes=len(plan.nodes),
            completed_nodes=sum(1 for s in state.node_statuses.values() if s == RuntimeNodeStatus.COMPLETED)
        )

        diagnostics = []
        for nid, ns in state.node_states.items():
            if ns.error_message:
                diagnostics.append(f"Node '{nid}' error: {ns.error_message}")

        result = ExecutionResult(
            plan_id=plan.plan_id,
            status=final_status,
            outputs=final_outputs,
            node_results=state.node_states,
            metrics=metrics,
            diagnostics=diagnostics
        )

        await self.context.event_bus.emit("runtime_finished", {
            "plan_id": plan.plan_id, 
            "status": final_status.value,
            "completed_nodes_count": metrics["success_rate"] * len(plan.nodes)
        })

        return result
