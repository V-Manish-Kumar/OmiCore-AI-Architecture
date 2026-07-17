import asyncio
from typing import Dict, Any, List
from omnicore.ir.models import TaskIR
from omnicore.optimizer.optimization_context import OptimizedExecutionDAG, OptimizedExecutionNode
from omnicore.communication.protocol import TaskSubmitMessage, TaskResultMessage
from omnicore.cluster.resource import ResourceRequirement
from omnicore.distributed.node_registry import NodeRegistry
from omnicore.distributed.load_balancer import LoadBalancer
from omnicore.distributed.dispatcher import TaskDispatcher
from omnicore.distributed.fault_tolerance import FaultToleranceManager
from omnicore.distributed.metrics import ClusterMetricsTracker
from omnicore.distributed.diagnostics import ClusterDiagnostics
from omnicore.distributed.autoscaling import Autoscaler
from omnicore.distributed.exceptions import ClusterError, ResourceExhaustedError

class DistributedScheduler:
    """
    Schedules and executes DAG workflows across available cluster workers.
    Resolves node dependencies, coordinates concurrent dispatches, and handles
    recovery attempts via the FaultToleranceManager.
    """
    def __init__(
        self,
        registry: NodeRegistry,
        load_balancer: LoadBalancer,
        dispatcher: TaskDispatcher,
        fault_manager: FaultToleranceManager,
        metrics: ClusterMetricsTracker,
        diagnostics: ClusterDiagnostics,
        autoscaler: Autoscaler
    ):
        self.registry = registry
        self.load_balancer = load_balancer
        self.dispatcher = dispatcher
        self.fault_manager = fault_manager
        self.metrics = metrics
        self.diagnostics = diagnostics
        self.autoscaler = autoscaler

    async def schedule(self, job_id: str, dag: OptimizedExecutionDAG, global_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronously schedules execution nodes.
        Tracks inter-node data flow and resolves ready tasks concurrently.
        """
        # Node states
        node_states = {nid: "PENDING" for nid in dag.topological_order}
        node_outputs = {}
        
        # Track node incoming dependency count
        in_degrees = {nid: 0 for nid in dag.topological_order}
        adjacency = {nid: [] for nid in dag.topological_order}
        
        # Build graph relationships
        nodes_map = {n.node_id: n for n in dag.nodes}
        # In this simplified model, sequential order is defined by topological_order index,
        # but let's build actual parents dependency:
        # If node has an input that matches the output of a prior node, there is a dependency edge!
        for i, nid in enumerate(dag.topological_order):
            node = nodes_map[nid]
            # Simple input matches prior output check
            for j in range(i):
                prior_id = dag.topological_order[j]
                prior_node = nodes_map[prior_id]
                if node.input == prior_node.output:
                    adjacency[prior_id].append(nid)
                    in_degrees[nid] += 1

        # Set up scheduling signals
        ready_queue = asyncio.Queue()
        for nid, deg in in_degrees.items():
            if deg == 0:
                await ready_queue.put(nid)

        active_jobs_count = 0
        error_occurred = None
        loop_lock = asyncio.Lock()

        async def worker_job(node_id: str):
            nonlocal active_jobs_count, error_occurred
            node = nodes_map[node_id]

            # 1. Resolve inputs
            node_input_val = global_inputs.get(node.input)
            # Check if input was produced by a parent node
            for prior_id in dag.topological_order:
                prior_node = nodes_map[prior_id]
                if node.input == prior_node.output and prior_id in node_outputs:
                    node_input_val = node_outputs[prior_id]
                    break

            # 2. Select Worker and Balancing Policy
            # Profile default resource requirement (CPU=0.5, Mem=128MB)
            req = ResourceRequirement(cpu_cores=0.5, memory_mb=128.0)

            # 3. Create Dispatch
            submit_msg = TaskSubmitMessage(
                job_id=job_id,
                node_id=node_id,
                capability=node.capability,
                inputs={node.input: node_input_val} if node_input_val is not None else {}
            )

            future = asyncio.get_running_loop().create_future()
            self.fault_manager.register_dispatch(
                job_id=job_id,
                node_id=node_id,
                worker_id="",  # Updated inside run_dispatch
                submit_msg=submit_msg,
                req=req,
                future=future
            )

            # 4. Dispatch and await completion
            start_time = asyncio.get_running_loop().time()
            
            # Helper dispatch trigger
            async def run_dispatch(nid: str, msg: TaskSubmitMessage, r: ResourceRequirement):
                async with loop_lock:
                    worker_id = self.load_balancer.select_worker(
                        node.capability, r, policy="least_loaded"
                    )
                self.diagnostics.log_event("SCHEDULE", f"Task '{nid}' scheduled on worker '{worker_id}'.")
                
                # Update active worker in registry dispatch details
                key = f"{msg.job_id}_{nid}"
                if key in self.fault_manager.inflight_dispatches:
                    self.fault_manager.inflight_dispatches[key]["worker_id"] = worker_id

                return await self.dispatcher.dispatch(worker_id, msg, r)

            # Tie the callback in fault manager to enable redistribution
            self.fault_manager.dispatch_task = run_dispatch

            # Trigger initial dispatch
            try:
                # Runs the actual dispatch and waits for result
                result_msg = await run_dispatch(node_id, submit_msg, req)
                # If dispatch timed out or disconnected, fault manager might override
                if not future.done():
                    future.set_result(result_msg)
            except Exception as e:
                if not future.done():
                    future.set_exception(e)

            # Wait for future completion (which could have been updated by fault recovery!)
            try:
                final_result = await future
            except Exception as e:
                final_result = TaskResultMessage(
                    job_id=job_id,
                    node_id=node_id,
                    success=False,
                    error_message=str(e),
                    worker_id=worker_id
                )

            # Cleanup
            self.fault_manager.deregister_dispatch(job_id, node_id)
            duration = asyncio.get_running_loop().time() - start_time

            async with loop_lock:
                if final_result.success:
                    node_states[node_id] = "COMPLETED"
                    self.metrics.record_completion(duration)
                    self.diagnostics.log_event("COMPLETED", f"Task '{node_id}' succeeded.")
                    
                    # Extract outputs
                    node_outputs[node_id] = final_result.outputs.get(node.output)
                    
                    # Propagate to children
                    for child in adjacency[node_id]:
                        in_degrees[child] -= 1
                        if in_degrees[child] == 0:
                            await ready_queue.put(child)
                else:
                    node_states[node_id] = "FAILED"
                    self.metrics.record_failure()
                    self.diagnostics.log_warning(f"Task '{node_id}' failed: {final_result.error_message}")
                    error_occurred = ClusterError(f"DAG failed at node '{node_id}': {final_result.error_message}")

        # Main Scheduling loop
        while any(state == "PENDING" for state in node_states.values()) and not error_occurred:
            # Trigger autoscaler check
            workers_list = [w for w in self.registry.workers.values()]
            self.autoscaler.evaluate(ready_queue.qsize(), workers_list)

            # Fetch ready nodes
            try:
                # Async wait with small timeout to check error flags
                node_to_run = await asyncio.wait_for(ready_queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                if error_occurred:
                    break
                # If no nodes ready but still pending, verify deadlocks
                if active_jobs_count == 0:
                    raise ClusterError("Deadlock detected. Dependency loop prevents scheduling progress.")
                continue

            node_states[node_to_run] = "RUNNING"
            active_jobs_count += 1
            # Spawn worker run task
            async def run_and_decrement(nid):
                nonlocal active_jobs_count
                try:
                    await worker_job(nid)
                finally:
                    active_jobs_count -= 1

            asyncio.create_task(run_and_decrement(node_to_run))

        # Wait for outstanding running tasks to settle
        while active_jobs_count > 0:
            await asyncio.sleep(0.05)

        if error_occurred:
            raise error_occurred

        return node_outputs
