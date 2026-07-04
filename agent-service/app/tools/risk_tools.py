from typing import Any

from app.schemas.review import ReviewRequest
from app.services.risk_model_service import RiskModelService


class RiskRuleTool:
    tool_name = "RiskRuleTool"

    def run(self, request: ReviewRequest) -> tuple[dict[str, Any], str]:
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

        rule_score = max(0, min(100, round(score)))
        if rule_score >= 80:
            rule_level = "LOW"
        elif rule_score >= 60:
            rule_level = "MEDIUM"
        else:
            rule_level = "HIGH"

        if not reasons:
            reasons.append("Income, debt, overdue, and material indicators are within the first-round mock policy range.")

        return {
            "rule_score": rule_score,
            "rule_level": rule_level,
            "rule_reasons": reasons,
            "debt_income_ratio": round(debt_income_ratio, 4),
        }, f"Rule score {rule_score}, level {rule_level}"


class RiskModelTool:
    tool_name = "RiskModelTool"
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

    def run(self, request: ReviewRequest, debt_income_ratio: float) -> tuple[dict[str, Any], str]:
        model_features = self._build_model_features(request, debt_income_ratio)
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
            }, "ML model unavailable; rule fallback will be used"
        return {
            "model_used": True,
            "model_risk_probability": result["model_risk_probability"],
            "model_risk_level": result["model_risk_label"],
            "model_version": result["model_version"],
            "model_features_used": result["features_used"],
            "model_explanation": result["explanation"],
            "model_error": None,
        }, f"Model probability {result['model_risk_probability']}, level {result['model_risk_label']}"

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
