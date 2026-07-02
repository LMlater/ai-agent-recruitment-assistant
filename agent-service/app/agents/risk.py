from typing import Any

from app.agents.base import BaseAgent
from app.schemas.review import ReviewRequest
from app.services.risk_model_service import RiskModelService


class RiskAgent(BaseAgent):
    agent_name = "RiskAgent"
    model_feature_names = [
        "age",
        "monthly_income",
        "work_years",
        "existing_debt",
        "overdue_count",
        "asset_proof_count",
        "amount",
        "term_months",
        "debt_income_ratio",
    ]

    def __init__(self, risk_model_service: RiskModelService | None = None) -> None:
        self.risk_model_service = risk_model_service or RiskModelService()

    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
        request: ReviewRequest = state["request"]
        customer = request.customer
        loan = request.loan_application

        rule_assessment = self._score_rules(request)
        model_features = self._build_model_features(request, rule_assessment["debt_income_ratio"])
        model_signal = self._predict_with_fallback(model_features)
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
            },
            "Run rule-based credit risk scoring and optional ML model signal",
            output_summary,
        )

    def _score_rules(self, request: ReviewRequest) -> dict[str, Any]:
        customer = request.customer
        loan = request.loan_application

        score = 100
        reasons: list[str] = []

        overdue_penalty = customer.overdue_count * 12
        if overdue_penalty:
            score -= overdue_penalty
            reasons.append(f"Overdue count {customer.overdue_count} reduces score by {overdue_penalty}.")

        annual_income = max(customer.monthly_income * 12, 1)
        debt_income_ratio = customer.existing_debt / annual_income
        if debt_income_ratio > 0.8:
            score -= 25
            reasons.append("Debt-to-income ratio is above 80%.")
        elif debt_income_ratio > 0.6:
            score -= 15
            reasons.append("Debt-to-income ratio is above 60%.")
        elif debt_income_ratio > 0.4:
            score -= 12
            reasons.append("Debt-to-income ratio is above 40%.")
        elif debt_income_ratio > 0.25:
            score -= 6
            reasons.append("Debt-to-income ratio is slightly elevated.")

        if customer.work_years < 1:
            score -= 10
            reasons.append("Work history is shorter than one year.")

        if loan.amount > customer.monthly_income * 24:
            score -= 25
            reasons.append("Requested amount is above 24 months of income.")
        elif loan.amount > customer.monthly_income * 12:
            score -= 12
            reasons.append("Requested amount is above 12 months of income.")

        if customer.asset_proof_count >= 3:
            score += 5
            reasons.append("Multiple asset proofs improve repayment confidence.")
        elif customer.asset_proof_count >= 1:
            score += 2
            reasons.append("Asset proof was provided.")

        risk_score = max(0, min(100, round(score)))
        if risk_score >= 80:
            risk_level = "LOW"
            suggested_amount = loan.amount
        elif risk_score >= 60:
            risk_level = "MEDIUM"
            suggested_amount = min(loan.amount, customer.monthly_income * 10)
        else:
            risk_level = "HIGH"
            suggested_amount = min(loan.amount, customer.monthly_income * 6)

        if not reasons:
            reasons.append("Income, debt, overdue, and material indicators are within the first-round mock policy range.")

        return {
            "rule_score": risk_score,
            "rule_level": risk_level,
            "rule_reasons": reasons,
            "debt_income_ratio": round(debt_income_ratio, 4),
        }

    def _build_model_features(self, request: ReviewRequest, debt_income_ratio: float) -> dict[str, float]:
        customer = request.customer
        loan = request.loan_application
        features = {
            "age": float(customer.age),
            "monthly_income": float(customer.monthly_income),
            "work_years": float(customer.work_years),
            "existing_debt": float(customer.existing_debt),
            "overdue_count": float(customer.overdue_count),
            "asset_proof_count": float(customer.asset_proof_count),
            "amount": float(loan.amount),
            "term_months": float(loan.term_months),
            "debt_income_ratio": float(debt_income_ratio),
        }
        return {name: features[name] for name in self.model_feature_names}

    def _predict_with_fallback(self, model_features: dict[str, float]) -> dict[str, Any]:
        try:
            result = self.risk_model_service.predict_risk(model_features)
        except Exception as exc:
            return {
                "model_used": False,
                "model_risk_probability": None,
                "model_risk_level": None,
                "model_version": None,
                "model_features_used": [],
                "model_explanation": [],
                "model_error": str(exc),
            }
        return {
            "model_used": True,
            "model_risk_probability": result["model_risk_probability"],
            "model_risk_level": result["model_risk_label"],
            "model_version": result["model_version"],
            "model_features_used": result["features_used"],
            "model_explanation": result["explanation"],
            "model_error": None,
        }

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
