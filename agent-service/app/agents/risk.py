from typing import Any

from app.agents.base import BaseAgent
from app.schemas.review import ReviewRequest


class RiskAgent(BaseAgent):
    agent_name = "RiskAgent"

    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
        request: ReviewRequest = state["request"]
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

        risk_assessment = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "suggested_amount": suggested_amount,
            "debt_income_ratio": round(debt_income_ratio, 4),
            "reasons": reasons,
        }
        return (
            {
                "risk_assessment": risk_assessment,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "suggested_amount": suggested_amount,
            },
            "Run rule-based credit risk scoring",
            f"{risk_level} risk with score {risk_score}",
        )
