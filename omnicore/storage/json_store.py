import os
import json
from typing import List, Optional, Dict, Any
from omnicore.storage.storage_interface import StorageInterface
from omnicore.models.cached_plan import CachedPlan
from omnicore.models.execution_record import ExecutionRecord

class JSONStore(StorageInterface):
    """
    Flat JSON-file-backed implementation of StorageInterface.
    Useful for local configurations and database-free operations.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._init_store()

    def _init_store(self) -> None:
        directory = os.path.dirname(os.path.abspath(self.filepath))
        if directory:
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self.filepath):
            self._write_raw({"plans": {}, "records": []})

    def _read_raw(self) -> Dict[str, Any]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"plans": {}, "records": []}

    def _write_raw(self, data: Dict[str, Any]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def save_plan(self, plan: CachedPlan) -> None:
        data = self._read_raw()
        data["plans"][plan.plan_id] = json.loads(plan.model_dump_json())
        self._write_raw(data)

    def get_plan(self, plan_id: str) -> Optional[CachedPlan]:
        data = self._read_raw()
        plan_dict = data["plans"].get(plan_id)
        if plan_dict:
            return CachedPlan.model_validate(plan_dict)
        return None

    def list_plans(self) -> List[CachedPlan]:
        data = self._read_raw()
        plans = []
        for plan_dict in data["plans"].values():
            plans.append(CachedPlan.model_validate(plan_dict))
        return plans

    def delete_plan(self, plan_id: str) -> None:
        data = self._read_raw()
        if plan_id in data["plans"]:
            del data["plans"][plan_id]
            self._write_raw(data)

    def save_record(self, record: ExecutionRecord) -> None:
        data = self._read_raw()
        record_dict = json.loads(record.model_dump_json())
        # Append or replace record based on record_id
        records_list = data["records"]
        updated = False
        for idx, rec in enumerate(records_list):
            if rec.get("record_id") == record.record_id:
                records_list[idx] = record_dict
                updated = True
                break
        if not updated:
            records_list.append(record_dict)
        self._write_raw(data)

    def list_records(self) -> List[ExecutionRecord]:
        data = self._read_raw()
        records = []
        for rec_dict in data["records"]:
            records.append(ExecutionRecord.model_validate(rec_dict))
        return records

    def clear(self) -> None:
        self._write_raw({"plans": {}, "records": []})
