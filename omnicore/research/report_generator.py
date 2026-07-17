import json
from typing import Dict, Any

class ReportGenerator:
    """
    Renders benchmarking comparison reports into Markdown, JSON, CSV, and HTML formats.
    """
    @staticmethod
    def to_markdown(comparison: Dict[str, Any]) -> str:
        """Generates a Markdown comparative report table."""
        name_a = comparison.get("config_a", "Config A")
        name_b = comparison.get("config_b", "Config B")
        
        lines = [
            f"# OmniCore Experiment Comparison Report",
            f"Comparing: **{name_a}** (A) vs **{name_b}** (B)\n",
            "| Phase | Mean A (sec) | Mean B (sec) | Speedup (%) |",
            "|---|---|---|---|---|"
        ]
        
        comps = comparison.get("comparisons", {})
        for phase, data in comps.items():
            lines.append(
                f"| {phase.capitalize()} | {data['mean_a']:.5f} | {data['mean_b']:.5f} | {data['speedup_percentage']}% |"
            )
            
        return "\n".join(lines)

    @staticmethod
    def to_json(comparison: Dict[str, Any]) -> str:
        """Generates raw JSON report output."""
        return json.dumps(comparison, indent=2)

    @staticmethod
    def to_csv(comparison: Dict[str, Any]) -> str:
        """Generates a flat CSV report string."""
        lines = ["phase,mean_a,mean_b,speedup_percentage"]
        comps = comparison.get("comparisons", {})
        for phase, data in comps.items():
            lines.append(f"{phase},{data['mean_a']},{data['mean_b']},{data['speedup_percentage']}")
        return "\n".join(lines)

    @staticmethod
    def to_html(comparison: Dict[str, Any]) -> str:
        """Generates a clean HTML report table."""
        name_a = comparison.get("config_a", "Config A")
        name_b = comparison.get("config_b", "Config B")
        
        rows = []
        comps = comparison.get("comparisons", {})
        for phase, data in comps.items():
            rows.append(f"""
            <tr>
                <td>{phase.capitalize()}</td>
                <td>{data['mean_a']:.5f}</td>
                <td>{data['mean_b']:.5f}</td>
                <td>{data['speedup_percentage']}%</td>
            </tr>
            """)
            
        return f"""
        <html>
        <head><title>OmniCore Benchmark Comparison</title></head>
        <body>
            <h2>OmniCore Comparative Report</h2>
            <p>Comparing <strong>{name_a}</strong> vs <strong>{name_b}</strong></p>
            <table border="1">
                <thead>
                    <tr>
                        <th>Phase</th>
                        <th>Mean A (s)</th>
                        <th>Mean B (s)</th>
                        <th>Speedup (%)</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </body>
        </html>
        """
