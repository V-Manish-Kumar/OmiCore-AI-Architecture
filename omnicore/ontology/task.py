from typing import Dict, Any
from pydantic import BaseModel, Field

class OntologyTask(BaseModel):
    """
    Semantic definition of a goal, task, or execution block.
    """
    task_id: str
    user_goal: str
    intent: str
    complexity: str = "Medium"
    properties: Dict[str, Any] = Field(default_factory=dict)
