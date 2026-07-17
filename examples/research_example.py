import sys
import os
import json

# Ensure the root package directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omnicore.research.experiment_config import ExperimentConfig
from omnicore.research.experiment_manager import ExperimentManager
from omnicore.research.comparison_engine import ComparisonEngine
from omnicore.research.report_generator import ReportGenerator

def main():
    print("=" * 80)
    print("OMNICORE RESEARCH & EXPERIMENTATION FRAMEWORK SHOWCASE")
    print("=" * 80)

    # 1. Instantiate ExperimentManager
    manager = ExperimentManager()

    # 2. Configure Run A: Baseline Configuration
    config_a = ExperimentConfig(
        experiment_name="Baseline Compiler Config",
        runs_count=3,
        workload_type="chain",
        workload_size=3,
        scheduler_policy="least_loaded"
    )

    # 3. Configure Run B: Optimized Configuration (with simulated optimization changes)
    config_b = ExperimentConfig(
        experiment_name="Optimized Custom Config",
        runs_count=3,
        workload_type="chain",
        workload_size=3,
        scheduler_policy="resource_aware"
    )

    print("\n[1] Running Baseline Experiment (3 runs, chain of 3 nodes)...")
    run_a = manager.run_experiment(config_a)
    print("  >>> Baseline stats parsing mean: ", run_a["metrics"]["parsing"]["mean"], "seconds")

    print("\n[2] Running Optimized Experiment (3 runs, chain of 3 nodes)...")
    run_b = manager.run_experiment(config_b)
    print("  >>> Optimized stats parsing mean: ", run_b["metrics"]["parsing"]["mean"], "seconds")

    # 4. Compare runs
    print("\n[3] Calculating latency speedups and variations...")
    comparison = ComparisonEngine.compare_experiments(run_a, run_b)

    # 5. Generate Markdown and HTML reports
    print("\n[4] Rendering Statistical Comparison Report (Markdown):")
    md_report = ReportGenerator.to_markdown(comparison)
    print("-" * 60)
    print(md_report)
    print("-" * 60)

    print("\n[5] Saving comparison raw JSON log...")
    raw_json = ReportGenerator.to_json(comparison)
    print("Exported JSON structure:")
    print(raw_json)
    
    print("\nShowcase execution completed successfully.")

if __name__ == "__main__":
    main()
