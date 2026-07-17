import pytest
import json
from omnicore.research.experiment_config import ExperimentConfig
from omnicore.research.workload_generator import WorkloadGenerator
from omnicore.research.statistical_analysis import StatisticalAnalyst
from omnicore.research.benchmark_runner import BenchmarkRunner
from omnicore.research.experiment_manager import ExperimentManager
from omnicore.research.comparison_engine import ComparisonEngine
from omnicore.research.report_generator import ReportGenerator
from omnicore.plugins.registry import PluginRegistry

# --- Tests ---

def test_workload_generation():
    """Verify programmatic workload chain and parallel node configurations."""
    # 1. Chain Generator
    chain_dag = WorkloadGenerator.generate_chain(3)
    assert len(chain_dag.nodes) == 3
    assert chain_dag.topological_order == ["n0", "n1", "n2"]
    assert chain_dag.nodes[0].input == "start"
    assert chain_dag.nodes[1].input == "out_0"
    assert chain_dag.nodes[2].input == "out_1"

    # 2. Parallel Generator
    parallel_dag = WorkloadGenerator.generate_parallel(4)
    assert len(parallel_dag.nodes) == 4
    assert len(parallel_dag.topological_order) == 4


def test_statistical_calculations():
    """Verify mathematical means, medians, standard errors, and percentiles."""
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    stats = StatisticalAnalyst.calculate_stats(values)

    assert stats["mean"] == 3.0
    assert stats["median"] == 3.0
    # Sample variance: sum((x - 3)^2) / 4 = (4 + 1 + 0 + 1 + 4)/4 = 2.5. Stddev = sqrt(2.5) = 1.58114
    assert stats["stddev"] == pytest.approx(1.58114, rel=1e-3)
    assert stats["p50"] == 3.0
    assert stats["p90"] == 4.6
    assert stats["stderr"] == pytest.approx(1.58114 / 2.23607, rel=1e-3)


def test_benchmark_runner_and_manager():
    """Verify runner runs iterations and outputs averages metrics."""
    config = ExperimentConfig(
        experiment_name="baseline_test",
        runs_count=2,
        workload_size=2,
        workload_type="chain"
    )
    dag = WorkloadGenerator.generate_chain(2)
    
    runner = BenchmarkRunner()
    metrics = runner.run_workload(config, dag)
    
    assert "parsing" in metrics
    assert "optimization" in metrics
    assert "execution" in metrics
    assert len(metrics["parsing"]) == 2
    assert all(t > 0 for t in metrics["parsing"])

    # Test ExperimentManager
    manager = ExperimentManager()
    exp_res = manager.run_experiment(config)
    
    assert exp_res["config"]["experiment_name"] == "baseline_test"
    assert "parsing" in exp_res["metrics"]
    assert exp_res["metrics"]["parsing"]["mean"] > 0


def test_comparison_and_reports():
    """Verify comparison engine calculations and multiformat report generation."""
    run_a = {
        "config": {"experiment_name": "Baseline"},
        "metrics": {
            "parsing": {"mean": 0.10},
            "optimization": {"mean": 0.05},
            "execution": {"mean": 0.50}
        }
    }
    run_b = {
        "config": {"experiment_name": "Optimized"},
        "metrics": {
            "parsing": {"mean": 0.08},
            "optimization": {"mean": 0.04},
            "execution": {"mean": 0.25}
        }
    }

    comp = ComparisonEngine.compare_experiments(run_a, run_b)
    
    # Verify speedup calculations
    # Parsing: (0.1 - 0.08)/0.1 * 100 = 20%
    assert comp["comparisons"]["parsing"]["speedup_percentage"] == 20.0
    # Execution: (0.5 - 0.25)/0.5 * 100 = 50%
    assert comp["comparisons"]["execution"]["speedup_percentage"] == 50.0

    # Verify Report formats
    md_report = ReportGenerator.to_markdown(comp)
    assert "OmniCore Experiment Comparison Report" in md_report
    assert "Parsing" in md_report
    assert "20.0%" in md_report

    json_report = ReportGenerator.to_json(comp)
    assert json.loads(json_report)["config_a"] == "Baseline"

    csv_report = ReportGenerator.to_csv(comp)
    assert "parsing,0.1,0.08,20.0" in csv_report

    html_report = ReportGenerator.to_html(comp)
    assert "<html>" in html_report
    assert "20.0%" in html_report


def test_plugin_registry():
    """Verify modular plugin registrations are independent of core models."""
    registry = PluginRegistry.get_instance()
    
    class MockPass:
        pass
    class MockScheduler:
        pass

    registry.register_optimizer_pass("mock_pass", MockPass)
    registry.register_scheduler("mock_scheduler", MockScheduler)

    assert registry.get_optimizer_pass("mock_pass") is MockPass
    assert registry.get_scheduler("mock_scheduler") is MockScheduler
    
    # Cleanup
    registry.clear()
