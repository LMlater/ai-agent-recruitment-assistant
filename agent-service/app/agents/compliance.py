from typing import Any

from app.agents.base import BaseAgent


class ComplianceAgent(BaseAgent):
    agent_name = "ComplianceAgent"

    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
        warnings = [
            "AI output is an approval assistance suggestion only; final approval must be performed manually.",
            "Audit records must be retained for review workflow traceability.",
        ]
        risk_level = state.get("risk_level")
        if risk_level == "HIGH":
            warnings.append("High-risk customer must enter manual senior review before any business decision.")
        if state.get("required_materials"):
            warnings.append("Missing or invalid materials require supplementary material handling.")

        return (
            {"compliance_warnings": warnings},
            "Check AI decision boundaries and audit requirements",
            "Compliance guardrails prepared",
        )
