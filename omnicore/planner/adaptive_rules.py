from typing import List
from omnicore.ir.models import TaskIR
from omnicore.ir.enums import Capability
from omnicore.planner.diagnostics import PlannerDiagnostic, PlannerDiagnosticSeverity

class AdaptiveRulesEngine:
    """
    Evaluates safety rules, no-output warnings, and critical path bottlenecks to emit diagnostics.
    """
    @staticmethod
    def evaluate_rules(task_ir: TaskIR) -> List[PlannerDiagnostic]:
        diagnostics = []

        # 1. No output warning rule
        if not task_ir.outputs:
            diagnostics.append(PlannerDiagnostic(
                severity=PlannerDiagnosticSeverity.WARNING,
                message="No global task outputs defined.",
                suggestion="Compiler pruning may eliminate non-side-effect nodes. Define outputs if values are required."
            ))

        # 2. Side-effect warnings (Email, DB writes)
        if Capability.EMAIL in task_ir.required_capabilities:
            diagnostics.append(PlannerDiagnostic(
                severity=PlannerDiagnosticSeverity.RISK_ASSESSMENT,
                message="Task involves automated email transmissions.",
                suggestion="Double-check variables and recipients to avoid sending spam/accidental notifications."
            ))
            
        if Capability.DATABASE_ACCESS in task_ir.required_capabilities:
            diagnostics.append(PlannerDiagnostic(
                severity=PlannerDiagnosticSeverity.RISK_ASSESSMENT,
                message="Task contains database write operations.",
                suggestion="Verify credentials and permissions to prevent unauthorized updates."
            ))

        # 3. High latency warning (Reasoning, CodeGen)
        high_latency_caps = {Capability.REASONING, Capability.CODE_GENERATION}
        found_heavy = high_latency_caps.intersection(set(task_ir.required_capabilities))
        if found_heavy:
            caps_str = ", ".join(c.value for c in found_heavy)
            diagnostics.append(PlannerDiagnostic(
                severity=PlannerDiagnosticSeverity.NOTE,
                message=f"Heavy computational tasks required: {caps_str}.",
                suggestion="Ensure client timeouts are set to at least 30 seconds."
            ))

        return diagnostics
