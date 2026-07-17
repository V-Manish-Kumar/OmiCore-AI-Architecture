import asyncio
from typing import Dict, Any
from omnicore.ir.enums import Capability

class CapabilityAdapter:
    """
    Abstract Base Class for all capability execution adapters.
    Adapters map abstract compiler capabilities to model/tool providers.
    """
    async def execute(self, capability: Capability, inputs: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Executes a task node's abstract capability with supplied inputs.
        Must be implemented by concrete adapters.
        """
        raise NotImplementedError("Capability adapters must implement compile-time execute method.")


class MockCapabilityAdapter(CapabilityAdapter):
    """
    Simulated implementation of CapabilityAdapter.
    Used for local testing and validation without invoking external LLMs/Services.
    """
    def __init__(self, latency: float = 0.05):
        self.latency = latency

    async def execute(self, capability: Capability, inputs: Dict[str, Any], context: Any) -> Dict[str, Any]:
        # Introduce simulated network/processing latency
        if self.latency > 0:
            await asyncio.sleep(self.latency)

        # Basic mock output patterns based on capability type
        if capability == Capability.WEB_SEARCH:
            return {"findings": f"Mock web search results for inputs {inputs}"}
            
        elif capability == Capability.COMPARISON:
            return {"comparison": f"Mock comparison analysis based on inputs {inputs}"}
            
        elif capability == Capability.SUMMARIZATION:
            return {"summary": f"Mock summary generated from inputs {inputs}"}
            
        elif capability == Capability.CODE_GENERATION:
            return {"code": f"def hello_world():\n    print('Hello World from inputs {inputs}')"}
            
        elif capability == Capability.REPORT_GENERATION:
            return {"report": f"Mock report formatted from inputs {inputs}"}
            
        elif capability == Capability.EMAIL:
            return {"email_receipt": f"Mock email dispatched successfully with inputs {inputs}"}
            
        elif capability == Capability.PDF_GENERATION:
            return {"pdf": f"Mock PDF binary generated successfully with inputs {inputs}"}
            
        elif capability == Capability.DATABASE_ACCESS:
            return {"database_result": f"Mock database records selected matching inputs {inputs}"}
            
        elif capability == Capability.RETRIEVAL:
            return {"retrieved_docs": f"Mock localized retrieved chunks for inputs {inputs}"}
            
        elif capability == Capability.REASONING:
            return {"reasoning_chain": f"Mock step-by-step reasoning logic for inputs {inputs}"}
            
        else:
            return {"result": f"Mock fallback output for capability '{capability.value}' with inputs {inputs}"}
