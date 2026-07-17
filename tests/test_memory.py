import os
import tempfile
import pytest
import time
from typing import List
from omnicore.ir.enums import Capability, TaskIntent
from omnicore.ir.models import TaskIR
from omnicore.optimizer.optimization_context import OptimizedExecutionNode, OptimizedExecutionDAG
from omnicore.models.cached_plan import CachedPlan
from omnicore.models.execution_record import ExecutionRecord
from omnicore.storage.sqlite_store import SQLiteStore
from omnicore.storage.json_store import JSONStore
from omnicore.memory.procedural_memory import ProceduralMemory
from omnicore.memory.cache import PlanLRUCache
from omnicore.memory.similarity import calculate_similarity, generate_signature
from omnicore.memory.ranking import score_candidate, rank_plans
from omnicore.memory.versioning import COMPILER_VERSION, is_compatible, validate_version
from omnicore.memory.exceptions import VersionMismatchError

# --- Test Helpers ---

def create_task_ir(goal: str, caps: List[Capability], constraints: List[str] = None) -> TaskIR:
    return TaskIR(
        task_id="task_test_123",
        primary_intent=TaskIntent.RESEARCH,
        domain="General",
        user_goal=goal,
        inputs=["query"],
        outputs=["summary"],
        constraints=constraints or [],
        required_capabilities=caps
    )

def create_execution_dag() -> OptimizedExecutionDAG:
    node = OptimizedExecutionNode(
        node_id="search_1",
        name="Search",
        description="Search info",
        capability=Capability.WEB_SEARCH,
        input="query",
        output="findings"
    )
    return OptimizedExecutionDAG(
        nodes=[node],
        topological_order=["search_1"]
    )

# --- Unit Tests ---

def test_sqlite_and_json_backends():
    """Verify storing and retrieving plans and records in both backends."""
    task_ir = create_task_ir("Search servers", [Capability.WEB_SEARCH])
    dag = create_execution_dag()
    
    plan = CachedPlan(
        plan_id="plan_1",
        normalized_signature="sig_1",
        task_ir=task_ir,
        execution_dag=dag
    )
    
    record = ExecutionRecord(
        task_id="task_test_123",
        plan_id="plan_1",
        normalized_signature="sig_1",
        task_ir=task_ir,
        execution_dag=dag,
        execution_time=1.5,
        cost=0.01,
        tokens=500,
        confidence=1.0,
        success_rate=1.0
    )

    # 1. Test SQLite Store
    sqlite_store = SQLiteStore(":memory:")
    sqlite_store.save_plan(plan)
    sqlite_store.save_record(record)
    
    assert sqlite_store.get_plan("plan_1") is not None
    assert len(sqlite_store.list_plans()) == 1
    assert len(sqlite_store.list_records()) == 1

    # 2. Test JSON Store
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = os.path.join(tmpdir, "memory_db.json")
        json_store = JSONStore(json_path)
        json_store.save_plan(plan)
        json_store.save_record(record)
        
        assert json_store.get_plan("plan_1") is not None
        assert len(json_store.list_plans()) == 1
        assert len(json_store.list_records()) == 1
        
        # Test deletion
        json_store.delete_plan("plan_1")
        assert json_store.get_plan("plan_1") is None


def test_signature_generation():
    """Verify that deterministic task signatures are correctly generated."""
    t1 = create_task_ir("Search web servers", [Capability.WEB_SEARCH], ["brief"])
    t2 = create_task_ir("Search web servers", [Capability.WEB_SEARCH], ["brief"])
    
    sig1 = generate_signature(t1)
    sig2 = generate_signature(t2)
    assert sig1 == sig2
    assert "intent:Research" in sig1
    assert "caps:web_search" in sig1


def test_similarity_scoring():
    """Verify that structural similarity calculations align semantics."""
    # 1. Identical meaning, slightly different goal text should have high similarity
    t1 = create_task_ir("Summarize this PDF file", [Capability.SUMMARIZATION, Capability.PDF_GENERATION])
    t2 = create_task_ir("Create a summary of the document", [Capability.SUMMARIZATION, Capability.PDF_GENERATION])
    
    similarity = calculate_similarity(t1, t2)
    # They share intents and capabilities and synonyms, so similarity should exceed 0.85
    assert similarity >= 0.85

    # 2. Different capabilities should have low similarity
    t3 = create_task_ir("Search and email", [Capability.WEB_SEARCH, Capability.EMAIL])
    assert calculate_similarity(t1, t3) < 0.60


def test_lru_cache_eviction():
    """Verify LRU cache capacity eviction and statistics."""
    cache = PlanLRUCache(capacity=2)
    
    task_ir = create_task_ir("Search", [Capability.WEB_SEARCH])
    dag = create_execution_dag()
    
    p1 = CachedPlan(plan_id="p1", normalized_signature="sig", task_ir=task_ir, execution_dag=dag)
    p2 = CachedPlan(plan_id="p2", normalized_signature="sig", task_ir=task_ir, execution_dag=dag)
    p3 = CachedPlan(plan_id="p3", normalized_signature="sig", task_ir=task_ir, execution_dag=dag)
    
    cache.put(p1)
    cache.put(p2)
    assert cache.get("p1") is not None
    
    # Adding p3 should evict p2 (since p1 was just accessed/retrieved)
    cache.put(p3)
    
    assert cache.get("p1") is not None
    assert cache.get("p2") is None # Evicted
    assert cache.get("p3") is not None
    
    stats = cache.get_statistics()
    assert stats["hits"] == 3
    assert stats["misses"] == 1
    assert stats["hit_rate"] > 0.60


def test_plan_ranking_logic():
    """Verify plan candidates prioritize higher success rates and lower latency."""
    task_ir = create_task_ir("Search", [Capability.WEB_SEARCH])
    dag = create_execution_dag()
    
    p1 = CachedPlan(plan_id="plan_1", normalized_signature="sig", task_ir=task_ir, execution_dag=dag)
    p2 = CachedPlan(plan_id="plan_2", normalized_signature="sig", task_ir=task_ir, execution_dag=dag)
    
    # record 1: success, fast
    r1 = ExecutionRecord(
        task_id="t1", plan_id="plan_1", normalized_signature="sig", task_ir=task_ir, execution_dag=dag,
        execution_time=1.0, cost=0.01, tokens=500, confidence=1.0, success_rate=1.0
    )
    # record 2: failure, slow
    r2 = ExecutionRecord(
        task_id="t2", plan_id="plan_2", normalized_signature="sig", task_ir=task_ir, execution_dag=dag,
        execution_time=5.0, cost=0.01, tokens=500, confidence=1.0, success_rate=0.5
    )
    
    candidates = [(p1, 0.9), (p2, 0.9)]
    records = [r1, r2]
    
    ranked = rank_plans(candidates, records)
    # plan_1 should rank higher due to 1.0 success rate and 1.0s latency vs 0.5 success and 5.0s latency
    assert ranked[0][0].plan_id == "plan_1"


def test_version_validation():
    """Verify that version checking successfully identifies mismatching plans."""
    task_ir = create_task_ir("Search", [Capability.WEB_SEARCH])
    dag = create_execution_dag()
    
    compatible_plan = CachedPlan(
        plan_id="plan_compat", normalized_signature="sig", task_ir=task_ir, execution_dag=dag,
        compiler_version=COMPILER_VERSION, optimizer_version=COMPILER_VERSION
    )
    incompatible_plan = CachedPlan(
        plan_id="plan_old", normalized_signature="sig", task_ir=task_ir, execution_dag=dag,
        compiler_version="0.5.0", optimizer_version="0.5.0"
    )
    
    assert is_compatible(compatible_plan) is True
    assert is_compatible(incompatible_plan) is False
    
    with pytest.raises(VersionMismatchError):
        validate_version(incompatible_plan)


def test_procedural_memory_lifecycle():
    """Verify store, retrieve, invalidate, and statistics cycles in memory API."""
    store = SQLiteStore(":memory:")
    memory = ProceduralMemory(store)
    
    task_ir = create_task_ir("Search web servers", [Capability.WEB_SEARCH])
    dag = create_execution_dag()
    
    record = ExecutionRecord(
        task_id="task_test_123",
        plan_id="plan_test_abc",
        normalized_signature="sig_abc",
        task_ir=task_ir,
        execution_dag=dag,
        execution_time=0.8,
        cost=0.0,
        tokens=0,
        confidence=1.0,
        success_rate=1.0
    )
    
    # Store record
    memory.store(record)
    
    # Retrieve should hit the cached plan
    retrieved = memory.retrieve(task_ir)
    assert retrieved is not None
    assert retrieved.plan_id == "plan_test_abc"
    
    # Invalidate should clear it
    memory.invalidate("plan_test_abc")
    assert memory.retrieve(task_ir) is None
    
    # Check stats
    stats = memory.statistics()
    assert stats["total_plans_stored"] == 0
    assert stats["total_execution_records_stored"] == 1 # record log is kept for history
