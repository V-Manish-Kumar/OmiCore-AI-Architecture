from pydantic import BaseModel

class MemoryMetadata(BaseModel):
    """
    Configuration parameters for memory storage and eviction policies.
    """
    lru_capacity: int = 100
    compiler_version: str = "1.0.0"
    schema_version: str = "1.0.0"
    optimizer_version: str = "1.0.0"
