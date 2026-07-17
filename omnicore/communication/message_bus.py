import asyncio
from typing import Dict, List, Callable, Any

class LocalMessageBus:
    """
    In-memory asynchronous Publish/Subscribe broker enabling transport-independent
    communication between coordinate schedulers and workers.
    """
    _instance = None

    @classmethod
    def get_instance(cls) -> "LocalMessageBus":
        if cls._instance is None:
            cls._instance = LocalMessageBus()
        return cls._instance

    def __init__(self):
        # Maps topic names to lists of subscriber callbacks
        self.subscribers: Dict[str, List[Callable[[str], Any]]] = {}

    def subscribe(self, topic: str, callback: Callable[[str], Any]) -> None:
        """Registers a subscriber callback for a topic."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)

    def unsubscribe(self, topic: str, callback: Callable[[str], Any]) -> None:
        """Unregisters a subscriber callback for a topic."""
        if topic in self.subscribers:
            try:
                self.subscribers[topic].remove(callback)
            except ValueError:
                pass

    async def publish(self, topic: str, message: str) -> None:
        """
        Publishes a message to all subscribers of a topic.
        Triggers subscriber callbacks asynchronously.
        """
        callbacks = self.subscribers.get(topic, [])
        if not callbacks:
            return

        # Fire callbacks in parallel async tasks to avoid blocking the publisher
        tasks = []
        for cb in callbacks:
            if asyncio.iscoroutinefunction(cb):
                tasks.append(asyncio.create_task(cb(message)))
            else:
                # Call synchronous callback directly
                cb(message)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def clear(self) -> None:
        """Clears all subscriptions."""
        self.subscribers.clear()
