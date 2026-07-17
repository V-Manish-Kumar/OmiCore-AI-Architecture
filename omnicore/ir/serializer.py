import json
from typing import Dict, Any, Union
from omnicore.ir.models import TaskIR, ExecutionDAG

def serialize_to_dict(model: Union[TaskIR, ExecutionDAG]) -> Dict[str, Any]:
    """Serializes the given TaskIR or ExecutionDAG model to a dictionary."""
    return model.model_dump()

def serialize_to_json(model: Union[TaskIR, ExecutionDAG], indent: int = 2) -> str:
    """Serializes the given TaskIR or ExecutionDAG model to a JSON string."""
    return model.model_dump_json(indent=indent)

def deserialize_task_ir(data: Union[str, Dict[str, Any]]) -> TaskIR:
    """Deserializes a JSON string or dictionary to a TaskIR instance."""
    if isinstance(data, str):
        return TaskIR.model_validate_json(data)
    return TaskIR.model_validate(data)

def deserialize_execution_dag(data: Union[str, Dict[str, Any]]) -> ExecutionDAG:
    """Deserializes a JSON string or dictionary to an ExecutionDAG instance."""
    if isinstance(data, str):
        return ExecutionDAG.model_validate_json(data)
    return ExecutionDAG.model_validate(data)
