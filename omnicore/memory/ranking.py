import time
from typing import List, Tuple
from omnicore.models.cached_plan import CachedPlan
from omnicore.models.execution_record import ExecutionRecord
from omnicore.memory.versioning import COMPILER_VERSION, OPTIMIZER_VERSION

def score_candidate(
    plan: CachedPlan, 
    similarity_score: float, 
    records: List[ExecutionRecord]
) -> float:
    """
    Computes a quality score between 0.0 and 1.0 for a plan candidate.
    Factors:
    - Task similarity (60% weight)
    - Success rate of previous runs (20% weight)
    - Version compatibility (10% weight)
    - Latency performance (5% weight)
    - Recency of execution (5% weight)
    """
    # 1. Success rate & latency averages
    success_rate = 1.0
    avg_latency = 0.0
    
    plan_records = [r for r in records if r.plan_id == plan.plan_id]
    if plan_records:
        success_rate = sum(r.success_rate for r in plan_records) / len(plan_records)
        avg_latency = sum(r.execution_time for r in plan_records) / len(plan_records)

    # 2. Version compatibility
    compat_score = 1.0
    if plan.compiler_version != COMPILER_VERSION or plan.optimizer_version != OPTIMIZER_VERSION:
        compat_score = 0.1

    # 3. Recency (decays over days)
    delta_time = max(0.0, time.time() - plan.timestamp)
    # 86400 seconds = 1 day half-life factor
    recency_score = 1.0 / (1.0 + (delta_time / 86400.0))

    # 4. Latency factor (faster is better; maps to range [0, 1])
    latency_score = 1.0 / (1.0 + avg_latency)

    # Weighted composite score
    rank_score = (
        (0.60 * similarity_score) +
        (0.20 * success_rate) +
        (0.10 * compat_score) +
        (0.05 * recency_score) +
        (0.05 * latency_score)
    )
    return round(rank_score, 4)

def rank_plans(
    candidates: List[Tuple[CachedPlan, float]], 
    records: List[ExecutionRecord]
) -> List[Tuple[CachedPlan, float]]:
    """
    Ranks plan candidates.
    Returns a sorted list of (CachedPlan, rank_score) tuples, descending.
    """
    scored = []
    for plan, similarity in candidates:
        score = score_candidate(plan, similarity, records)
        scored.append((plan, score))
    # Sort by score descending
    return sorted(scored, key=lambda x: x[1], reverse=True)
