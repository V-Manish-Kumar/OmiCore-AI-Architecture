from typing import List, Optional
from omnicore.models.cached_plan import CachedPlan
from omnicore.models.execution_record import ExecutionRecord

class StorageInterface:
    """
    Abstract interface for Procedural Memory pluggable storage engines.
    """
    def save_plan(self, plan: CachedPlan) -> None:
        """Saves a compiled CachedPlan to the store."""
        raise NotImplementedError()

    def get_plan(self, plan_id: str) -> Optional[CachedPlan]:
        """Retrieves a CachedPlan by its ID."""
        raise NotImplementedError()

    def list_plans(self) -> List[CachedPlan]:
        """Lists all CachedPlans saved in the store."""
        raise NotImplementedError()

    def delete_plan(self, plan_id: str) -> None:
        """Deletes a CachedPlan from the store by its ID."""
        raise NotImplementedError()

    def save_record(self, record: ExecutionRecord) -> None:
        """Saves an ExecutionRecord log entry."""
        raise NotImplementedError()

    def list_records(self) -> List[ExecutionRecord]:
        """Lists all ExecutionRecords saved in the store."""
        raise NotImplementedError()

    def clear(self) -> None:
        """Deletes all plans and records from the store."""
        raise NotImplementedError()
