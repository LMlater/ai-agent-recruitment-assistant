from typing import Any


class ComplianceGuardrailTool:
    tool_name = "ComplianceGuardrailTool"

    def run(self, state: dict[str, Any]) -> tuple[dict[str, Any], str]:
        warnings = [
            "AI output is an approval assistance suggestion only; final approval must be performed manually.",
            "ML model output is an auxiliary signal and must be reviewed with rule reasons and policy references.",
            "Audit records must be retained for review workflow traceability.",
        ]
        risk_level = state.get("risk_level")
        if risk_level == "HIGH":
            warnings.append("High-risk customer must enter manual senior review before any business decision.")
        if state.get("required_materials"):
            warnings.append("Missing or invalid materials require supplementary material handling.")

        return {"compliance_warnings": warnings}, "Compliance guardrails prepared"
