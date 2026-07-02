from typing import Any

from app.agents.base import BaseAgent
from app.schemas.review import ReviewRequest
from app.services.policy_retrieval_service import PolicyRetrievalService


class PolicyAgent(BaseAgent):
    agent_name = "PolicyAgent"

    def __init__(self, policy_retrieval_service: PolicyRetrievalService | None = None) -> None:
        self.policy_retrieval_service = policy_retrieval_service or PolicyRetrievalService()

    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
        query = self._build_query(state)
        references = self.policy_retrieval_service.search(query, top_k=5)
        serialized_references = [reference.model_dump() for reference in references]
        return (
            {"policy_references": serialized_references},
            "Run RAG policy retrieval over mock credit policy documents",
            f"Retrieved {len(serialized_references)} policy references",
        )

    def _build_query(self, state: dict[str, Any]) -> str:
        request: ReviewRequest = state["request"]
        customer = request.customer
        loan = request.loan_application
        risk_assessment = state.get("risk_assessment", {})

        query_parts = [
            loan.purpose,
            f"amount {loan.amount:g}",
            f"term {loan.term_months} months",
            f"risk level {state.get('risk_level', 'UNKNOWN')}",
            f"risk score {state.get('risk_score', 'UNKNOWN')}",
            f"applicant age {customer.age}",
            f"monthly income {customer.monthly_income:g}",
            f"work years {customer.work_years:g}",
            f"existing debt {customer.existing_debt:g}",
            f"overdue count {customer.overdue_count}",
            f"asset proof count {customer.asset_proof_count}",
            f"debt income ratio {risk_assessment.get('debt_income_ratio', 'UNKNOWN')}",
            "manual review",
            "AI cannot auto approve",
            "ML model auxiliary",
            "final manual approval",
            "audit trace",
        ]

        if state.get("risk_level") in {"MEDIUM", "HIGH"}:
            query_parts.append("medium high risk manual review")
        query_parts.extend(risk_assessment.get("rule_reasons", []))
        query_parts.extend(risk_assessment.get("reasons", []))
        query_parts.extend(state.get("required_materials", []))
        query_parts.extend(state.get("compliance_warnings", []))

        if risk_assessment.get("model_used"):
            query_parts.extend(
                [
                    f"model risk probability {risk_assessment.get('model_risk_probability')}",
                    f"model risk level {risk_assessment.get('model_risk_level')}",
                    f"model version {risk_assessment.get('model_version')}",
                ]
            )
        else:
            query_parts.append("ML model unavailable rule fallback")

        return " | ".join(str(part) for part in query_parts if part)
