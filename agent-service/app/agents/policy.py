from typing import Any

from app.agents.base import BaseAgent
from app.services.retrieval_service import RetrievalService


class PolicyAgent(BaseAgent):
    agent_name = "PolicyAgent"

    def __init__(self, retrieval_service: RetrievalService | None = None) -> None:
        self.retrieval_service = retrieval_service or RetrievalService()

    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
        risk_level = state.get("risk_level", "UNKNOWN")
        query_terms = ["AI", "manual review", "debt", "overdue", risk_level.lower()]
        references = self.retrieval_service.search(query_terms)
        return (
            {"policy_references": references},
            "Search mock credit approval policies by keyword",
            f"Retrieved {len(references)} mock policy references",
        )
