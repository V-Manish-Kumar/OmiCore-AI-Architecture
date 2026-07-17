from pydantic import BaseModel
from typing import Dict
from omnicore.ir.enums import Capability

class CapabilityProfile(BaseModel):
    """
    Typical resource requirements and latency baseline profiles for a Capability.
    """
    runtime_seconds: float
    token_usage: int
    memory_mb: float
    tool_invocations: int
    network_ops: int
    expected_retries: float

# Baseline heuristic profiles
CAPABILITY_PROFILES: Dict[Capability, CapabilityProfile] = {
    Capability.WEB_SEARCH: CapabilityProfile(
        runtime_seconds=8.0, token_usage=600, memory_mb=64.0, tool_invocations=1, network_ops=3, expected_retries=0.1
    ),
    Capability.CODE_GENERATION: CapabilityProfile(
        runtime_seconds=12.0, token_usage=1500, memory_mb=128.0, tool_invocations=0, network_ops=0, expected_retries=0.05
    ),
    Capability.SUMMARIZATION: CapabilityProfile(
        runtime_seconds=4.0, token_usage=1000, memory_mb=64.0, tool_invocations=0, network_ops=0, expected_retries=0.02
    ),
    Capability.COMPARISON: CapabilityProfile(
        runtime_seconds=5.0, token_usage=800, memory_mb=64.0, tool_invocations=0, network_ops=0, expected_retries=0.02
    ),
    Capability.TRANSLATION: CapabilityProfile(
        runtime_seconds=3.0, token_usage=500, memory_mb=64.0, tool_invocations=0, network_ops=0, expected_retries=0.02
    ),
    Capability.REASONING: CapabilityProfile(
        runtime_seconds=15.0, token_usage=2000, memory_mb=256.0, tool_invocations=0, network_ops=0, expected_retries=0.08
    ),
    Capability.RETRIEVAL: CapabilityProfile(
        runtime_seconds=2.0, token_usage=400, memory_mb=64.0, tool_invocations=1, network_ops=1, expected_retries=0.02
    ),
    Capability.REPORT_GENERATION: CapabilityProfile(
        runtime_seconds=10.0, token_usage=3000, memory_mb=128.0, tool_invocations=0, network_ops=0, expected_retries=0.02
    ),
    Capability.EMAIL: CapabilityProfile(
        runtime_seconds=1.5, token_usage=300, memory_mb=32.0, tool_invocations=1, network_ops=1, expected_retries=0.15
    ),
    Capability.PDF_GENERATION: CapabilityProfile(
        runtime_seconds=6.0, token_usage=500, memory_mb=128.0, tool_invocations=0, network_ops=0, expected_retries=0.02
    ),
    Capability.DATABASE_ACCESS: CapabilityProfile(
        runtime_seconds=2.0, token_usage=200, memory_mb=64.0, tool_invocations=1, network_ops=1, expected_retries=0.05
    ),
    Capability.UNKNOWN: CapabilityProfile(
        runtime_seconds=5.0, token_usage=500, memory_mb=64.0, tool_invocations=0, network_ops=0, expected_retries=0.05
    )
}
