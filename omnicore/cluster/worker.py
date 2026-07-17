import asyncio
import time
from typing import List, Dict, Any, Optional
from omnicore.ir.enums import Capability
from omnicore.cluster.resource import ResourceState
from omnicore.communication.message_bus import LocalMessageBus
from omnicore.communication.serializer import Serializer
from omnicore.communication.protocol import (
    WorkerRegisterMessage, 
    HeartbeatMessage, 
    TaskSubmitMessage, 
    TaskResultMessage
)

class ClusterWorker:
    """
    Cluster worker node that advertises resources, listens for dispatched tasks,
    executes capability workloads, and publishes health heartbeats.
    """
    def __init__(
        self, 
        worker_id: str, 
        capabilities: List[Capability], 
        resources: ResourceState, 
        bus: Optional[LocalMessageBus] = None,
        heartbeat_interval: float = 0.5
    ):
        self.worker_id = worker_id
        self.capabilities = capabilities
        self.resources = resources
        self.bus = bus or LocalMessageBus.get_instance()
        self.heartbeat_interval = heartbeat_interval
        
        self.is_running = False
        self._heartbeat_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Starts worker heartbeat loops and registers with coordinator."""
        self.is_running = True
        
        # 1. Register with coordinator
        reg_msg = WorkerRegisterMessage(
            worker_id=self.worker_id,
            resources=self.resources,
            capabilities=self.capabilities
        )
        await self.bus.publish("cluster_registrations", Serializer.serialize(reg_msg))

        # 2. Subscribe to worker tasks topic
        self.bus.subscribe(f"worker_tasks_{self.worker_id}", self._receive_task)

        # 3. Start sending heartbeats
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def stop(self) -> None:
        """Stops worker health loops and unsubscribes from broker."""
        self.is_running = False
        
        self.bus.unsubscribe(f"worker_tasks_{self.worker_id}", self._receive_task)
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # Publish unregistration event
        await self.bus.publish("cluster_unregistrations", self.worker_id)

    async def _heartbeat_loop(self) -> None:
        """Periodically publishes worker heartbeat status signals."""
        while self.is_running:
            try:
                hb = HeartbeatMessage(
                    worker_id=self.worker_id,
                    cpu_utilization=self.resources.allocated_cpu_cores / self.resources.total_cpu_cores,
                    memory_utilization=self.resources.allocated_memory_mb / self.resources.total_memory_mb,
                    timestamp=time.time()
                )
                await self.bus.publish("worker_heartbeats", Serializer.serialize(hb))
                await asyncio.sleep(self.heartbeat_interval)
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    async def _receive_task(self, msg_str: str) -> None:
        """Processes and executes a task payload."""
        submit_msg = Serializer.deserialize(msg_str, TaskSubmitMessage)
        
        # Simulate simple task runtime execution delay (e.g. 0.05 seconds)
        await asyncio.sleep(0.05)
        
        success = True
        outputs = {}
        err_msg = None

        # Resolve output key matching
        # Let's echo input back or generate mock outputs
        try:
            for key, val in submit_msg.inputs.items():
                # E.g. input key "query" -> output key "findings" or "summary"
                # Mock result payload
                outputs["findings"] = f"Results for: {val}"
                outputs["summary"] = f"Summary of search: {val}"
                outputs["output"] = f"Result payload of {submit_msg.capability.value}"
        except Exception as e:
            success = False
            err_msg = str(e)

        # Publish task execution result back to transient task completion topic
        result_msg = TaskResultMessage(
            job_id=submit_msg.job_id,
            node_id=submit_msg.node_id,
            success=success,
            outputs=outputs,
            error_message=err_msg,
            worker_id=self.worker_id
        )
        
        result_topic = f"task_result_{submit_msg.job_id}_{submit_msg.node_id}"
        await self.bus.publish(result_topic, Serializer.serialize(result_msg))
class BrokenWorker(ClusterWorker):
    """Worker that silent-fails or drops tasks for fault-tolerance checks."""
    async def _receive_task(self, msg_str: str) -> None:
        # Intentionally do not reply to trigger timeout/heartbeat failure!
        pass
