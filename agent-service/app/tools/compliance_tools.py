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
        if state.get("senior_review_required"):
            warnings.append("Senior manual review is required before final human approval action.")
            warnings.extend(state.get("senior_review_reasons", []))
        if state.get("required_materials"):
            warnings.append("Missing or invalid materials require supplementary material handling.")

        return {"compliance_warnings": warnings}, "Compliance guardrails prepared"


class SeniorReviewChecklistTool:
    tool_name = "SeniorReviewChecklistTool"

    def run(self, state: dict[str, Any]) -> tuple[dict[str, Any], str]:
        reasons = [
            "High risk level requires senior manual review.",
            "AI/ML output remains assistance only.",
        ]
        risk_assessment = state.get("risk_assessment", {})
        for reason in risk_assessment.get("rule_reasons", risk_assessment.get("reasons", []))[:2]:
            reasons.append(f"Rule risk reason for senior reviewer: {reason}")

        return {
            "senior_review_required": True,
            "senior_review_reasons": reasons,
        }, "Senior manual review checklist prepared"
