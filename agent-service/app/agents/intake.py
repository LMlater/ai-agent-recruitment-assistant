from typing import Any

from app.agents.base import BaseAgent
from app.schemas.review import ReviewRequest


class IntakeAgent(BaseAgent):
    agent_name = "IntakeAgent"

    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
        request: ReviewRequest = state["request"]
        required_materials: list[str] = []
        warnings: list[str] = []

        if request.customer.age < 18:
            required_materials.append("Applicant must be an adult borrower.")
        if request.customer.monthly_income <= 0:
            required_materials.append("Valid income proof is required.")
        if request.loan_application.amount <= 0:
            required_materials.append("Loan amount must be greater than zero.")
        if request.loan_application.term_months <= 0:
            required_materials.append("Loan term must be greater than zero.")
        if request.customer.asset_proof_count == 0:
            warnings.append("No asset proof was submitted; manual material review is recommended.")

        intake_check = {
            "complete": not required_materials,
            "warnings": warnings,
            "checked_fields": [
                "age",
                "monthly_income",
                "loan_amount",
                "term_months",
                "asset_proof_count",
            ],
        }
        output = "Required fields are complete" if not required_materials else "Supplementary materials are required"
        return (
            {
                "intake_check": intake_check,
                "required_materials": required_materials,
                "intake_warnings": warnings,
            },
            "Check customer basics and loan application materials",
            output,
        )
