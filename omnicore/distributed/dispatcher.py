import asyncio
import json
from typing import Dict, Any
from omnicore.communication.message_bus import LocalMessageBus
from omnicore.communication.serializer import Serializer
from omnicore.communication.protocol import TaskSubmitMessage, TaskResultMessage
from omnicore.cluster.resource import ResourceRequirement
from omnicore.distributed.resource_manager import ResourceManager

class TaskDispatcher:
    """
    Submits compiled execution tasks to designated worker queues via the MessageBus,
    tracks worker execution progress, and synchronizes resource release on completion.
    """
    def __init__(self, bus: LocalMessageBus, resource_manager: ResourceManager):
        self.bus = bus
        self.resource_manager = resource_manager

    async def dispatch(
        self, 
        worker_id: str, 
        submit_msg: TaskSubmitMessage, 
        requirement: ResourceRequirement,
        timeout: float = 30.0
    ) -> TaskResultMessage:
        """
        Locks worker resource capacity, submits task payload, and awaits execution completion signal.
        """
        # Lock resource capacity
        self.resource_manager.allocate_resources(worker_id, requirement)
        
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        result_topic = f"task_result_{submit_msg.job_id}_{submit_msg.node_id}"

        async def on_result(msg_str: str):
            try:
                result = Serializer.deserialize(msg_str, TaskResultMessage)
                if not future.done():
                    future.set_result(result)
            except Exception as e:
                if not future.done():
                    future.set_exception(e)

        # Subscribe to result topic before submitting task to prevent race conditions
        self.bus.subscribe(result_topic, on_result)

        # Publish task to target worker task queue
        worker_queue_topic = f"worker_tasks_{worker_id}"
        serialized_msg = Serializer.serialize(submit_msg)
        await self.bus.publish(worker_queue_topic, serialized_msg)

        try:
            # Await completion response
            result_msg = await asyncio.wait_for(future, timeout=timeout)
            return result_msg
        except asyncio.TimeoutError:
            return TaskResultMessage(
                job_id=submit_msg.job_id,
                node_id=submit_msg.node_id,
                success=False,
                error_message=f"Task execution timed out after {timeout}s.",
                worker_id=worker_id
            )
        finally:
            # Release resource capacity and unsubscribe
            self.resource_manager.release_resources(worker_id, requirement)
            self.bus.unsubscribe(result_topic, on_result)
