import asyncio
from typing import Dict, Any, List
from omnicore.execution.execution_plan import ExecutionPlan
from omnicore.execution.execution_node import RuntimeNodeStatus
from omnicore.runtime.runtime_state import RuntimeState
from omnicore.runtime.runtime_context import RuntimeContext
from omnicore.runtime.scheduler import RuntimeScheduler
from omnicore.runtime.worker import RuntimeWorker

class RuntimeExecutor:
    """
    Manages the runtime execution loop. Launches concurrent async worker tasks
    for nodes as soon as their dependencies are completed, handles cascading failures,
    and updates global execution progress.
    """
    def __init__(self, plan: ExecutionPlan, context: RuntimeContext):
        self.plan = plan
        self.context = context
        self.scheduler = RuntimeScheduler(plan)

    async def execute(self, state: RuntimeState) -> None:
        active_tasks: Dict[str, asyncio.Task] = {}
        
        while True:
            # Propagate cancellation check
            self.context.cancellation_token.throw_if_cancelled()
            
            # 1. Fetch nodes that are Ready (Pending and all dependencies Completed)
            ready_nodes = self.scheduler.get_ready_nodes(state)
            
            # 2. Filter out already executing nodes and launch workers
            nodes_to_launch = [nid for nid in ready_nodes if nid not in active_tasks]
            for nid in nodes_to_launch:
                worker = RuntimeWorker(nid, self.context)
                task = asyncio.create_task(worker.execute(state))
                active_tasks[nid] = task
                
            # 3. Check for cascaded dependency failures (marks downstream nodes FAILED)
            self.scheduler.check_cascade_failures(state)
            
            # 4. If no running tasks and no new ready nodes, scheduling is complete
            if not active_tasks:
                break
                
            # 5. Wait for at least one worker task to complete
            done, pending = await asyncio.wait(
                active_tasks.values(),
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # 6. Retrieve results and clean up active tasks
            for task in done:
                # Find the node ID belonging to this task
                finished_node_id = next(nid for nid, t in active_tasks.items() if t == task)
                del active_tasks[finished_node_id]
                
                try:
                    # Propagate worker exception if one occurred
                    task.result()
                except Exception:
                    # Workers record their own failure state.
                    # We continue the schedule loop so other independent tasks can run
                    # and cascaded dependency failures are propagated down failed paths.
                    pass
