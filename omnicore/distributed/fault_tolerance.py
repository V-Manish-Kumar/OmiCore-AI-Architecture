import logging
from typing import Dict, Any, Callable, Optional
from omnicore.communication.protocol import TaskSubmitMessage, TaskResultMessage
from omnicore.cluster.resource import ResourceRequirement
from omnicore.distributed.exceptions import WorkerNotFoundError, ResourceExhaustedError

class FaultToleranceManager:
    """
    Tracks in-flight task dispatches and implements failure recovery redistribution policies.
    """
    def __init__(self, dispatch_task_callback: Callable[[str, TaskSubmitMessage, ResourceRequirement], Any]):
        # Callback to trigger a fresh task dispatch
        self.dispatch_task = dispatch_task_callback
        # Maps (job_id, node_id) -> task details for outstanding executions
        self.inflight_dispatches: Dict[str, Dict[str, Any]] = {}

    def register_dispatch(
        self, 
        job_id: str, 
        node_id: str, 
        worker_id: str, 
        submit_msg: TaskSubmitMessage, 
        req: ResourceRequirement,
        future: Any,
        max_attempts: int = 3
    ) -> None:
        key = f"{job_id}_{node_id}"
        self.inflight_dispatches[key] = {
            "job_id": job_id,
            "node_id": node_id,
            "worker_id": worker_id,
            "submit_msg": submit_msg,
            "requirement": req,
            "future": future,
            "attempts": 1,
            "max_attempts": max_attempts
        }

    def deregister_dispatch(self, job_id: str, node_id: str) -> None:
        key = f"{job_id}_{node_id}"
        if key in self.inflight_dispatches:
            del self.inflight_dispatches[key]

    def handle_worker_failure(self, failed_worker_id: str) -> None:
        """
        Scans outstanding dispatches on failed_worker_id and reschedules them on alternative nodes.
        """
        for key, disp in list(self.inflight_dispatches.items()):
            if disp["worker_id"] == failed_worker_id:
                future = disp["future"]
                if future.done():
                    continue

                # Check retry attempts
                if disp["attempts"] < disp["max_attempts"]:
                    disp["attempts"] += 1
                    
                    # Spawn reschedule task in background
                    import asyncio
                    asyncio.create_task(self._reschedule_task(disp))
                else:
                    # Exceeded maximum retries, fail task
                    result = TaskResultMessage(
                        job_id=disp["job_id"],
                        node_id=disp["node_id"],
                        success=False,
                        error_message=f"Task failed after worker '{failed_worker_id}' disconnected.",
                        worker_id=failed_worker_id
                    )
                    future.set_result(result)

    async def _reschedule_task(self, disp: Dict[str, Any]) -> None:
        """Helper to find another worker and dispatch task again."""
        job_id = disp["job_id"]
        node_id = disp["node_id"]
        req = disp["requirement"]
        submit_msg = disp["submit_msg"]
        future = disp["future"]

        try:
            # We trigger the callback which selects worker and runs dispatch
            result = await self.dispatch_task(node_id, submit_msg, req)
            if not future.done():
                future.set_result(result)
        except Exception as e:
            if not future.done():
                # Wrap error
                result = TaskResultMessage(
                    job_id=job_id,
                    node_id=node_id,
                    success=False,
                    error_message=f"Failed to reschedule task: {e}",
                    worker_id=disp["worker_id"]
                )
                future.set_result(result)
