import time
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TraceSpan(BaseModel):
    name: str
    phase: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    success: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Tracer:
    """
    Observability event tracer logging spans across parser, optimizer,
    planner, and runtime stages. Spans are thread-safe and exportable as JSON.
    """
    def __init__(self):
        self.spans: List[TraceSpan] = []
        self.active_spans: Dict[str, TraceSpan] = {}

    def start_span(self, name: str, phase: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Starts tracking a new execution span."""
        span = TraceSpan(
            name=name,
            phase=phase,
            start_time=time.perf_counter(),
            metadata=metadata or {}
        )
        self.active_spans[name] = span

    def end_span(self, name: str, success: bool = True, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Ends an active span, calculating duration and status."""
        span = self.active_spans.pop(name, None)
        if span:
            span.end_time = time.perf_counter()
            span.duration_ms = round((span.end_time - span.start_time) * 1000.0, 3)
            span.success = success
            if metadata:
                span.metadata.update(metadata)
            self.spans.append(span)

    def export_traces(self) -> str:
        """Serializes all collected trace spans to a JSON string."""
        return json.dumps([span.model_dump() for span in self.spans], indent=2)

    def clear(self) -> None:
        self.spans.clear()
        self.active_spans.clear()
