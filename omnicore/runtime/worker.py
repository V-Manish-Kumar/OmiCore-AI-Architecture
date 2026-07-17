import time
import asyncio
from typing import Dict, Any
from omnicore.execution.execution_node import RuntimeNodeStatus, ExecutionNodeState
from omnicore.runtime.runtime_state import RuntimeState
from omnicore.runtime.runtime_context import RuntimeContext
from omnicore.runtime.exceptions import NodeExecutionError, PermanentNodeError
from omnicore.runtime.checkpoint import save_checkpoint

class RuntimeWorker:
    """
    Executes a single execution node.
    Manages node lifecycle state transitions, adapter execution, backoff retries,
    cancellation monitoring, and checkpoints.
    """
    def __init__(self, node_id: str, context: RuntimeContext):
        self.node_id = node_id
        self.context = context

    async def execute(self, state: RuntimeState) -> Dict[str, Any]:
        node_state = state.node_states[self.node_id]
        node = node_state.node

        # 1. Transition to READY
        node_state.status = RuntimeNodeStatus.READY
        state.node_statuses[self.node_id] = RuntimeNodeStatus.READY
        self.context.cancellation_token.throw_if_cancelled()

        # 2. Transition to RUNNING
        node_state.status = RuntimeNodeStatus.RUNNING
        state.node_statuses[self.node_id] = RuntimeNodeStatus.RUNNING
        node_state.started_at = time.perf_counter()
        self.context.metrics_tracker.record_node_start(self.node_id)
        
        await self.context.event_bus.emit("node_started", {"node_id": self.node_id, "capability": node.capability.value})

        attempt = 0
        outputs = {}

        # Resolve inputs from state variables
        inputs_list = node.input or []
        if isinstance(inputs_list, str):
            inputs_list = [inputs_list]
        inputs_dict = {sym: state.variables[sym] for sym in inputs_list if sym in state.variables}

        while True:
            try:
                self.context.cancellation_token.throw_if_cancelled()
                attempt += 1
                
                # Invoke the abstract capability adapter
                outputs = await self.context.adapter.execute(node.capability, inputs_dict, self.context)
                
                # Check cancellation again after execution
                self.context.cancellation_token.throw_if_cancelled()
                break

            except asyncio.CancelledError as ce:
                # Handle cancellation
                node_state.status = RuntimeNodeStatus.CANCELLED
                state.node_statuses[self.node_id] = RuntimeNodeStatus.CANCELLED
                self.context.metrics_tracker.record_node_cancelled_or_failed(self.node_id)
                await self.context.event_bus.emit("node_failed", {"node_id": self.node_id, "error": "Cancelled"})
                raise ce

            except Exception as e:
                # Record error statistics
                node_state.error_message = str(e)
                
                # Check retry policy
                if self.context.retry_policy.should_retry(e, attempt):
                    node_state.retry_count = attempt
                    self.context.metrics_tracker.record_retry()
                    
                    delay = self.context.retry_policy.get_delay(attempt)
                    
                    await self.context.event_bus.emit("node_failed", {
                        "node_id": self.node_id, 
                        "error": str(e), 
                        "retry_attempt": attempt,
                        "retry_delay_seconds": delay
                    })
                    
                    # Sleep with cancellation awareness
                    try:
                        await asyncio.sleep(delay)
                    except asyncio.CancelledError as ce:
                        node_state.status = RuntimeNodeStatus.CANCELLED
                        state.node_statuses[self.node_id] = RuntimeNodeStatus.CANCELLED
                        self.context.metrics_tracker.record_node_cancelled_or_failed(self.node_id)
                        raise ce
                    
                    continue
                else:
                    # Permanent/final execution failure
                    node_state.status = RuntimeNodeStatus.FAILED
                    state.node_statuses[self.node_id] = RuntimeNodeStatus.FAILED
                    self.context.metrics_tracker.record_node_cancelled_or_failed(self.node_id)
                    
                    await self.context.event_bus.emit("node_failed", {"node_id": self.node_id, "error": str(e)})
                    
                    raise NodeExecutionError(self.node_id, str(e), e)

        # 3. Execution succeeded - save outputs to global state variables
        # Map outputs to the state variables dict positionally or by key
        expected_outputs = node.output or []
        if isinstance(expected_outputs, str):
            expected_outputs = [expected_outputs]
            
        mapped_outputs = {}
        if len(expected_outputs) == 1 and len(outputs) == 1:
            val = list(outputs.values())[0]
            mapped_outputs[expected_outputs[0]] = val
        else:
            out_keys = list(outputs.keys())
            for idx, name in enumerate(expected_outputs):
                if name in outputs:
                    mapped_outputs[name] = outputs[name]
                elif idx < len(out_keys):
                    mapped_outputs[name] = outputs[out_keys[idx]]
                    
        for k, v in mapped_outputs.items():
            state.variables[k] = v

        node_state.output_data = mapped_outputs
        node_state.finished_at = time.perf_counter()
        node_state.execution_time = node_state.finished_at - node_state.started_at
        node_state.status = RuntimeNodeStatus.COMPLETED
        state.node_statuses[self.node_id] = RuntimeNodeStatus.COMPLETED

        self.context.metrics_tracker.record_node_finish(self.node_id)
        
        await self.context.event_bus.emit("node_completed", {"node_id": self.node_id, "outputs": list(outputs.keys())})

        # Save checkpoint after each node completes
        if self.context.checkpoint_filepath:
            save_checkpoint(state, self.context.checkpoint_filepath)

        return outputs
