import asyncio
import uuid
import json
from omnicore.communication.message_bus import LocalMessageBus

class RPCManager:
    """
    Enables Request/Reply patterns over a Pub/Sub message bus.
    Creates transient unique reply topics and awaits responses asynchronously.
    """
    def __init__(self, bus: LocalMessageBus):
        self.bus = bus

    async def call(self, request_topic: str, reply_topic_prefix: str, payload: str, timeout: float = 5.0) -> str:
        """
        Sends a request to request_topic and awaits a response on a transient reply topic.
        """
        reply_topic = f"{reply_topic_prefix}_{uuid.uuid4().hex}"
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        async def on_reply(msg: str):
            if not future.done():
                future.set_result(msg)

        self.bus.subscribe(reply_topic, on_reply)

        # Wrap payload with reply channel details
        envelope = {
            "reply_topic": reply_topic,
            "payload": payload
        }
        
        await self.bus.publish(request_topic, json.dumps(envelope))

        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response
        finally:
            self.bus.unsubscribe(reply_topic, on_reply)
