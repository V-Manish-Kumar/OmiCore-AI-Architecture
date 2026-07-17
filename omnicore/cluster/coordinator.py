from typing import Optional, TYPE_CHECKING
from omnicore.communication.message_bus import LocalMessageBus
from omnicore.communication.serializer import Serializer
from omnicore.communication.protocol import WorkerRegisterMessage

if TYPE_CHECKING:
    from omnicore.distributed.node_registry import NodeRegistry

class ClusterCoordinator:
    """
    Subscribes to cluster registrations/unregistrations and coordinates registry entries.
    """
    def __init__(self, registry: "NodeRegistry", bus: Optional[LocalMessageBus] = None):
        self.registry = registry
        self.bus = bus or LocalMessageBus.get_instance()

    async def start(self) -> None:
        """Subscribes to registration channels."""
        self.bus.subscribe("cluster_registrations", self._receive_registration)
        self.bus.subscribe("cluster_unregistrations", self._receive_unregistration)

    async def stop(self) -> None:
        """Unsubscribes from registration channels."""
        self.bus.unsubscribe("cluster_registrations", self._receive_registration)
        self.bus.unsubscribe("cluster_unregistrations", self._receive_unregistration)

    async def _receive_registration(self, msg_str: str) -> None:
        """Updates worker in registry upon receipt of registration message."""
        try:
            msg = Serializer.deserialize(msg_str, WorkerRegisterMessage)
            self.registry.register_worker(
                worker_id=msg.worker_id,
                resources=msg.resources,
                capabilities=msg.capabilities
            )
        except Exception:
            pass

    async def _receive_unregistration(self, worker_id: str) -> None:
        """Removes worker entry from registry upon worker shutdown."""
        self.registry.unregister_worker(worker_id)
