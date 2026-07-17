import time
import asyncio
from typing import Dict, Any, List, Callable, Union, Awaitable
from pydantic import BaseModel, Field

class Event(BaseModel):
    """
    Represents an execution event emitted by the EventBus.
    """
    event_type: str
    timestamp: float = Field(default_factory=time.time)
    data: Dict[str, Any] = Field(default_factory=dict)


class EventBus:
    """
    Asynchronous event bus supporting subscription callbacks and event emission.
    Supports '*' wildcard subscriptions to listen to all events.
    """
    def __init__(self):
        self._listeners: Dict[str, List[Callable[[Event], Any]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Event], Any]) -> None:
        """Subscribes a listener callback to the specified event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[Event], Any]) -> None:
        """Removes a listener callback from subscriptions."""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
            except ValueError:
                pass

    async def emit(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Emits an event asynchronously to all subscribed listeners.
        Resilient against callback exceptions.
        """
        event = Event(event_type=event_type, data=data)
        
        # Get matching listeners and wildcard listeners
        listeners = list(self._listeners.get(event_type, []))
        wildcards = list(self._listeners.get("*", []))
        all_listeners = listeners + wildcards

        for callback in all_listeners:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception:
                # Silently catch listener errors so they don't halt the core runtime execution
                pass
