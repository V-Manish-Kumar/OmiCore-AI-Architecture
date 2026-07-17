from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from omnicore.runtime.adapters.capability_adapter import CapabilityAdapter
from omnicore.runtime.cancellation import CancellationToken
from omnicore.runtime.event_bus import EventBus
from omnicore.runtime.metrics import RuntimeMetricsTracker
from omnicore.runtime.retry_policy import RetryPolicy

class RuntimeContext(BaseModel):
    """
    Groups dependencies and configurations required during execution.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    adapter: CapabilityAdapter
    cancellation_token: CancellationToken = Field(default_factory=CancellationToken)
    event_bus: EventBus = Field(default_factory=EventBus)
    metrics_tracker: RuntimeMetricsTracker = Field(default_factory=RuntimeMetricsTracker)
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    checkpoint_filepath: Optional[str] = None
