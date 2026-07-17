import sqlite3
import json
from typing import List, Optional
from omnicore.storage.storage_interface import StorageInterface
from omnicore.models.cached_plan import CachedPlan
from omnicore.models.execution_record import ExecutionRecord

class SQLiteStore(StorageInterface):
    """
    SQLite-backed implementation of StorageInterface.
    Stores index keys in queryable columns and model structures in JSON text.
    """
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return self._conn

    def close(self) -> None:
        """Closes the persistent database connection."""
        self._conn.close()

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            # Create plans table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS plans (
                    plan_id TEXT PRIMARY KEY,
                    normalized_signature TEXT,
                    compiler_version TEXT,
                    optimizer_version TEXT,
                    timestamp REAL,
                    serialized_data TEXT
                )
            """)
            # Create records table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    record_id TEXT PRIMARY KEY,
                    task_id TEXT,
                    plan_id TEXT,
                    normalized_signature TEXT,
                    execution_time REAL,
                    cost REAL,
                    tokens INTEGER,
                    confidence REAL,
                    success_rate REAL,
                    compiler_version TEXT,
                    runtime_version TEXT,
                    timestamp REAL,
                    serialized_data TEXT
                )
            """)
            conn.commit()

    def save_plan(self, plan: CachedPlan) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO plans 
                (plan_id, normalized_signature, compiler_version, optimizer_version, timestamp, serialized_data)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    plan.plan_id,
                    plan.normalized_signature,
                    plan.compiler_version,
                    plan.optimizer_version,
                    plan.timestamp,
                    plan.model_dump_json()
                )
            )
            conn.commit()

    def get_plan(self, plan_id: str) -> Optional[CachedPlan]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT serialized_data FROM plans WHERE plan_id = ?", (plan_id,)).fetchone()
            if row:
                return CachedPlan.model_validate_json(row["serialized_data"])
        return None

    def list_plans(self) -> List[CachedPlan]:
        plans = []
        with self._get_connection() as conn:
            rows = conn.execute("SELECT serialized_data FROM plans").fetchall()
            for row in rows:
                plans.append(CachedPlan.model_validate_json(row["serialized_data"]))
        return plans

    def delete_plan(self, plan_id: str) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM plans WHERE plan_id = ?", (plan_id,))
            conn.commit()

    def save_record(self, record: ExecutionRecord) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO records 
                (record_id, task_id, plan_id, normalized_signature, execution_time, cost, tokens, confidence, success_rate, compiler_version, runtime_version, timestamp, serialized_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.record_id,
                    record.task_id,
                    record.plan_id,
                    record.normalized_signature,
                    record.execution_time,
                    record.cost,
                    record.tokens,
                    record.confidence,
                    record.success_rate,
                    record.compiler_version,
                    record.runtime_version,
                    record.timestamp,
                    record.model_dump_json()
                )
            )
            conn.commit()

    def list_records(self) -> List[ExecutionRecord]:
        records = []
        with self._get_connection() as conn:
            rows = conn.execute("SELECT serialized_data FROM records").fetchall()
            for row in rows:
                records.append(ExecutionRecord.model_validate_json(row["serialized_data"]))
        return records

    def clear(self) -> None:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM plans")
            conn.execute("DELETE FROM records")
            conn.commit()
