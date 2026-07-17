from typing import List, Optional
from omnicore.storage.storage_interface import StorageInterface
from omnicore.models.cached_plan import CachedPlan
from omnicore.models.execution_record import ExecutionRecord
from omnicore.memory.exceptions import StorageError

class PlanRepository:
    """
    Repository abstraction isolating the storage backend from procedural memory logic.
    Handles data access errors and translates them to unified StorageErrors.
    """
    def __init__(self, store: StorageInterface):
        self.store = store

    def save_plan(self, plan: CachedPlan) -> None:
        try:
            self.store.save_plan(plan)
        except Exception as e:
            raise StorageError(f"Repository failed to save plan: {e}") from e

    def get_plan(self, plan_id: str) -> Optional[CachedPlan]:
        try:
            return self.store.get_plan(plan_id)
        except Exception as e:
            raise StorageError(f"Repository failed to fetch plan '{plan_id}': {e}") from e

    def list_plans(self) -> List[CachedPlan]:
        try:
            return self.store.list_plans()
        except Exception as e:
            raise StorageError(f"Repository failed to list plans: {e}") from e

    def delete_plan(self, plan_id: str) -> None:
        try:
            self.store.delete_plan(plan_id)
        except Exception as e:
            raise StorageError(f"Repository failed to delete plan '{plan_id}': {e}") from e

    def save_record(self, record: ExecutionRecord) -> None:
        try:
            self.store.save_record(record)
        except Exception as e:
            raise StorageError(f"Repository failed to save execution record: {e}") from e

    def list_records(self) -> List[ExecutionRecord]:
        try:
            return self.store.list_records()
        except Exception as e:
            raise StorageError(f"Repository failed to list execution records: {e}") from e

    def clear(self) -> None:
        try:
            self.store.clear()
        except Exception as e:
            raise StorageError(f"Repository failed to clear data: {e}") from e
