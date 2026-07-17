import time
from typing import List, Dict, Any, Optional, Tuple
from omnicore.storage.storage_interface import StorageInterface
from omnicore.models.cached_plan import CachedPlan
from omnicore.models.execution_record import ExecutionRecord
from omnicore.ir.models import TaskIR
from omnicore.memory.plan_repository import PlanRepository
from omnicore.memory.cache import PlanLRUCache
from omnicore.memory.metadata import MemoryMetricsTracker
from omnicore.memory.similarity import calculate_similarity, generate_signature
from omnicore.memory.ranking import rank_plans
from omnicore.memory.versioning import is_compatible

class ProceduralMemory:
    """
    Core Procedural Memory subsystem implementing query caching, similarity searches,
    plan ranking, version validation, and statistics reporting.
    """
    def __init__(self, store: StorageInterface, cache_capacity: int = 100):
        self.repository = PlanRepository(store)
        self.cache = PlanLRUCache(capacity=cache_capacity)
        self.tracker = MemoryMetricsTracker()

    def store(self, record: ExecutionRecord) -> None:
        """
        Stores an ExecutionRecord in repository history.
        Also caches/updates the associated Optimized CachedPlan.
        """
        # Save record log
        self.repository.save_record(record)

        # Check if the optimized plan is already saved
        plan = self.repository.get_plan(record.plan_id)
        if plan is None:
            plan = CachedPlan(
                plan_id=record.plan_id,
                normalized_signature=record.normalized_signature,
                task_ir=record.task_ir,
                execution_dag=record.execution_dag,
                compiler_version=record.compiler_version,
                optimizer_version=record.compiler_version
            )
            self.repository.save_plan(plan)

        # Update in LRU cache
        self.cache.put(plan)

    def retrieve(self, task_ir: TaskIR, similarity_threshold: float = 0.85) -> Optional[CachedPlan]:
        """
        Retrieves the highest quality matching execution plan for the given TaskIR.
        Applies version validation and updates optimization latency savings.
        """
        start_time = time.perf_counter()
        
        # Search candidates
        candidates = self.find_similar(task_ir, similarity_threshold)
        
        duration = time.perf_counter() - start_time
        self.tracker.record_retrieval(duration)

        if not candidates:
            return None

        # Return the best ranked candidate plan (rank_plans returns sorted list of (Plan, score))
        best_candidate, rank_score = candidates[0]
        
        # Verify compatibility
        if is_compatible(best_candidate):
            # Calculate estimated parse/optimization phase time saved
            self.tracker.record_reuse(time_saved=0.08)
            return best_candidate

        return None

    def find_similar(self, task_ir: TaskIR, threshold: float = 0.85) -> List[Tuple[CachedPlan, float]]:
        """
        Performs structural similarity search over saved plans.
        Filters candidates below threshold and returns ranked results.
        """
        plans = self.repository.list_plans()
        records = self.repository.list_records()
        
        candidates = []
        for plan in plans:
            sim = calculate_similarity(task_ir, plan.task_ir)
            if sim >= threshold:
                candidates.append((plan, sim))

        # Rank candidates using success, latencies, versions, and recency
        ranked = rank_plans(candidates, records)
        return ranked

    def invalidate(self, plan_id: str) -> None:
        """Removes a plan from the cache and repository."""
        self.cache.invalidate(plan_id)
        self.repository.delete_plan(plan_id)

    def statistics(self) -> Dict[str, Any]:
        """Compiles health metrics, hits, misses, and compilation time savings."""
        cache_stats = self.cache.get_statistics()
        tracker_stats = self.tracker.get_summary()
        
        plans = self.repository.list_plans()
        records = self.repository.list_records()
        
        return {
            "cache": cache_stats,
            "metrics": tracker_stats,
            "total_plans_stored": len(plans),
            "total_execution_records_stored": len(records)
        }
