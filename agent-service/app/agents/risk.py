from typing import Any

from app.agents.base import BaseAgent
from app.schemas.review import ReviewRequest
from app.services.risk_model_service import RiskModelService
from app.tools.risk_tools import RiskModelTool, RiskRuleTool
from app.tools.tool_runner import run_tool


class RiskAgent(BaseAgent):
    agent_name = "RiskAgent"

    def __init__(self, risk_model_service: RiskModelService | None = None) -> None:
        self.rule_tool = RiskRuleTool()
        self.model_tool = RiskModelTool(risk_model_service)

    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
        request: ReviewRequest = state["request"]
        customer = request.customer
        loan = request.loan_application

        rule_assessment, rule_tool_call = run_tool(
            tool_name=self.rule_tool.tool_name,
            input_summary="Score credit application with rule-based policy",
            operation=lambda: self.rule_tool.run(request),
        )
        model_signal, model_tool_call = run_tool(
            tool_name=self.model_tool.tool_name,
            input_summary="Run baseline credit risk model as auxiliary signal",
            operation=lambda: self.model_tool.run(request, rule_assessment["debt_income_ratio"]),
        )
        risk_score, risk_level = self._fuse_risk(rule_assessment, model_signal)
        suggested_amount = self._suggest_amount(risk_level, loan.amount, customer.monthly_income)

        risk_assessment = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "suggested_amount": suggested_amount,
            "rule_score": rule_assessment["rule_score"],
            "rule_level": rule_assessment["rule_level"],
            "rule_reasons": rule_assessment["rule_reasons"],
            "reasons": rule_assessment["rule_reasons"],
            "model_used": model_signal["model_used"],
            "model_risk_probability": model_signal["model_risk_probability"],
            "model_risk_level": model_signal["model_risk_level"],
            "model_version": model_signal["model_version"],
            "model_features_used": model_signal["model_features_used"],
            "model_explanation": model_signal["model_explanation"],
            "model_error": model_signal["model_error"],
            "fusion_strategy": (
                "final level takes the higher risk level from rule and model; "
                "final score = 0.65 * rule_score + 0.35 * model_score"
            ),
            "debt_income_ratio": rule_assessment["debt_income_ratio"],
        }
        tool_calls = [rule_tool_call.model_dump(), model_tool_call.model_dump()]
        output_summary = (
            f"{risk_level} risk with fused score {risk_score} using rule and model signal"
            if model_signal["model_used"]
            else f"{risk_level} risk with score {risk_score} using rule fallback because ML model is unavailable"
        )
        return (
            {
                "risk_assessment": risk_assessment,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "suggested_amount": suggested_amount,
                "tool_calls": tool_calls,
            },
            "Run rule-based credit risk scoring and optional ML model signal",
            output_summary,
        )

    def _fuse_risk(self, rule_assessment: dict[str, Any], model_signal: dict[str, Any]) -> tuple[int, str]:
        rule_score = rule_assessment["rule_score"]
        rule_level = rule_assessment["rule_level"]
        if not model_signal["model_used"]:
            return rule_score, rule_level

        model_score = round(100 * (1 - float(model_signal["model_risk_probability"])))
        final_score = max(0, min(100, round(0.65 * rule_score + 0.35 * model_score)))
        final_level = self._higher_risk_level(rule_level, model_signal["model_risk_level"])
        return final_score, final_level

    def _higher_risk_level(self, rule_level: str, model_level: str) -> str:
        order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        return rule_level if order[rule_level] >= order[model_level] else model_level

    def _suggest_amount(self, risk_level: str, requested_amount: float, monthly_income: float) -> float:
        if risk_level == "LOW":
            return requested_amount
        if risk_level == "MEDIUM":
            return min(requested_amount, monthly_income * 10)
        return min(requested_amount, monthly_income * 6)
