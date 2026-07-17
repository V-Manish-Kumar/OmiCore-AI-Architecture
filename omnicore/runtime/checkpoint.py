import os
from omnicore.runtime.runtime_state import RuntimeState
from omnicore.runtime.exceptions import CheckpointError

def save_checkpoint(state: RuntimeState, filepath: str) -> None:
    """Serializes the current RuntimeState and saves it to a file path."""
    try:
        directory = os.path.dirname(os.path.abspath(filepath))
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))
    except Exception as e:
        raise CheckpointError(f"Failed to save execution checkpoint to '{filepath}': {e}") from e

def load_checkpoint(filepath: str) -> RuntimeState:
    """Deserializes and restores a RuntimeState from a file path."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            json_data = f.read()
        return RuntimeState.model_validate_json(json_data)
    except Exception as e:
        raise CheckpointError(f"Failed to load execution checkpoint from '{filepath}': {e}") from e
