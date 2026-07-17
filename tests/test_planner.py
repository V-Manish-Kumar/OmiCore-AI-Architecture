import pytest
from typing import List
from omnicore.ir.enums import Capability, TaskIntent
from omnicore.ir.models import TaskIR
from omnicore.models.execution_strategy import ExecutionStrategy, StrategyConfig
from omnicore.models.execution_record import ExecutionRecord
from omnicore.optimizer.optimization_context import OptimizedExecutionNode, OptimizedExecutionDAG
from omnicore.planner.planner import AdaptivePlanner
from omnicore.planner.strategy_selector import StrategySelector
from omnicore.planner.cost_model import PlannerCostModel
from omnicore.planner.confidence_model import PlannerConfidenceModel
from omnicore.planner.execution_predictor import PlannerExecutionPredictor
from omnicore.planner.adaptive_rules import AdaptiveRulesEngine
from omnicore.planner.diagnostics import PlannerDiagnosticSeverity
from omnicore.memory.procedural_memory import ProceduralMemory
from omnicore.storage.sqlite_store import SQLiteStore

# --- Test Helpers ---

def create_task_ir(goal: str, caps: List[Capability], constraints: List[str] = None, outputs: List[str] = None) -> TaskIR:
    return TaskIR(
        task_id="task_plan_123",
        primary_intent=TaskIntent.RESEARCH,
        domain="General",
        user_goal=goal,
        inputs=["query"],
        outputs=["summary"] if outputs is None else outputs,
        constraints=constraints or [],
        required_capabilities=caps,
        confidence_score=0.9
    )

def create_execution_dag(caps: List[Capability]) -> OptimizedExecutionDAG:
    nodes = []
    for idx, cap in enumerate(caps):
        nodes.append(OptimizedExecutionNode(
            node_id=f"node_{idx}",
            name=f"Node {idx}",
            description="Details",
            capability=cap,
            input="in",
            output="out"
        ))
    return OptimizedExecutionDAG(
        nodes=nodes,
        topological_order=[n.node_id for n in nodes]
    )

# --- Unit Tests ---

def test_strategy_selector():
    """Verify strategy matching for constraints and capability counts."""
    # 1. Default for single capability should be SEQUENTIAL
    t_single = create_task_ir("Search only", [Capability.WEB_SEARCH])
    strategy, config = StrategySelector.select_strategy(t_single)
    assert strategy == ExecutionStrategy.SEQUENTIAL
    assert config.enable_parallel_execution is False

    # 2. Multi-capability default should be BALANCED
    t_multi = create_task_ir("Search and summarize", [Capability.WEB_SEARCH, Capability.SUMMARIZATION])
    strategy, config = StrategySelector.select_strategy(t_multi)
    assert strategy == ExecutionStrategy.BALANCED
    assert config.enable_parallel_execution is True

    # 3. Latency constraints should map to LATENCY_OPTIMIZED
    t_fast = create_task_ir("Search", [Capability.WEB_SEARCH, Capability.SUMMARIZATION], ["highly fast execution"])
    strategy, config = StrategySelector.select_strategy(t_fast)
    assert strategy == ExecutionStrategy.LATENCY_OPTIMIZED

    # 4. Budget constraints should map to LOW_COST
    t_cheap = create_task_ir("Search", [Capability.WEB_SEARCH, Capability.SUMMARIZATION], ["lowcost budget"])
    strategy, config = StrategySelector.select_strategy(t_cheap)
    assert strategy == ExecutionStrategy.LOW_COST

    # 5. Critical side-effects should map to HIGH_RELIABILITY
    t_rel = create_task_ir("Dispatch email", [Capability.WEB_SEARCH, Capability.EMAIL])
    strategy, config = StrategySelector.select_strategy(t_rel)
    assert strategy == ExecutionStrategy.HIGH_RELIABILITY


def test_strategy_selector_historical_failures():
    """Verify selector upgrades strategy to HIGH_RELIABILITY on poor history."""
    t_multi = create_task_ir("Search and summarize", [Capability.WEB_SEARCH, Capability.SUMMARIZATION])
    dag = create_execution_dag([Capability.WEB_SEARCH, Capability.SUMMARIZATION])
    
    # Store records with poor success rate
    store = SQLiteStore(":memory:")
    memory = ProceduralMemory(store)
    
    r1 = ExecutionRecord(
        task_id="t1", plan_id="p1", normalized_signature="sig", task_ir=t_multi, execution_dag=dag,
        execution_time=10.0, cost=0.01, tokens=500, confidence=1.0, success_rate=0.5 # 50% success
    )
    memory.store(r1)
    
    # Selector should check records and promote to HIGH_RELIABILITY
    strategy, config = StrategySelector.select_strategy(t_multi, memory)
    assert strategy == ExecutionStrategy.HIGH_RELIABILITY
    assert config.retry_max_attempts == 5


def test_cost_model_scaling():
    """Verify cost model sums baseline tokens and applies constraint scaling."""
    # 1. Baseline
    t_base = create_task_ir("Search", [Capability.WEB_SEARCH, Capability.SUMMARIZATION])
    res_base = PlannerCostModel.estimate_resources(t_base)
    # Search (600) + Summarize (1000) = 1600 tokens
    assert res_base["estimated_tokens"] == 1600
    assert res_base["estimated_cost"] > 0.0

    # 2. Detailed constraint (increase)
    t_detailed = create_task_ir("Search", [Capability.WEB_SEARCH, Capability.SUMMARIZATION], ["detailed extensive research"])
    res_det = PlannerCostModel.estimate_resources(t_detailed)
    assert res_det["estimated_tokens"] > 1600

    # 3. Simple constraint (decrease)
    t_simple = create_task_ir("Search", [Capability.WEB_SEARCH, Capability.SUMMARIZATION], ["simple brief summary"])
    res_simp = PlannerCostModel.estimate_resources(t_simple)
    assert res_simp["estimated_tokens"] < 1600


def test_confidence_model():
    """Verify confidence updates blending historical records."""
    t_base = create_task_ir("Search", [Capability.WEB_SEARCH])
    dag = create_execution_dag([Capability.WEB_SEARCH])
    
    store = SQLiteStore(":memory:")
    memory = ProceduralMemory(store)
    
    # Record with 100% success rate
    r1 = ExecutionRecord(
        task_id="t1", plan_id="p1", normalized_signature="sig", task_ir=t_base, execution_dag=dag,
        execution_time=2.0, cost=0.0, tokens=0, confidence=0.9, success_rate=1.0
    )
    memory.store(r1)
    
    # Blend: (0.7 * 0.9 base) + (0.3 * 1.0 success) = 0.63 + 0.3 = 0.93
    conf = PlannerConfidenceModel.predict_confidence(t_base, memory)
    assert conf == 0.93


def test_execution_predictor():
    """Verify parallel scheduling projections reduce runtime relative to sequential."""
    t_multi = create_task_ir("Search and summarize", [Capability.WEB_SEARCH, Capability.SUMMARIZATION])
    
    # Sequential estimation
    res_seq = PlannerExecutionPredictor.predict_execution(t_multi, enable_parallel=False)
    # Search (8.0s) + Summarize (4.0s) = 12.0s
    assert res_seq["estimated_runtime"] == 12.0

    # Parallel estimation (overlaps parallel capabilities)
    res_par = PlannerExecutionPredictor.predict_execution(t_multi, enable_parallel=True)
    # both are parallelizable, so parallel duration is max(8.0s, 4.0s) = 8.0s
    assert res_par["estimated_runtime"] == 8.0
    assert res_par["parallel_efficiency"] == 1.0
    assert "web_search" in res_par["bottlenecks"]


def test_adaptive_rules_warnings():
    """Verify diagnostic warnings for side-effects and empty outputs."""
    # 1. No output warning
    t_no_out = create_task_ir("Search", [Capability.WEB_SEARCH], outputs=[])
    diag1 = AdaptiveRulesEngine.evaluate_rules(t_no_out)
    severities = [d.severity for d in diag1]
    assert PlannerDiagnosticSeverity.WARNING in severities

    # 2. Automated email warning
    t_email = create_task_ir("Email report", [Capability.EMAIL])
    diag2 = AdaptiveRulesEngine.evaluate_rules(t_email)
    severities2 = [d.severity for d in diag2]
    assert PlannerDiagnosticSeverity.RISK_ASSESSMENT in severities2


# --- Integration Test ---

def test_planner_end_to_end_flow():
    """Verify overall planner orchestrations."""
    t_task = create_task_ir("Reason and compare and search", [Capability.REASONING, Capability.COMPARISON, Capability.WEB_SEARCH])
    planner = AdaptivePlanner()
    
    result = planner.plan(t_task)
    
    assert result.task_id == "task_plan_123"
    assert result.execution_strategy == ExecutionStrategy.BALANCED
    assert result.estimated_runtime > 0.0
    assert result.estimated_cost > 0.0
    assert result.estimated_tokens > 0
    assert len(result.recommended_passes) == 8
    assert len(result.diagnostics) >= 1
