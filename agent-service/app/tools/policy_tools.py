from typing import Any

from app.services.policy_retrieval_service import PolicyRetrievalService


class PolicySearchTool:
    tool_name = "PolicySearchTool"

    def __init__(self, policy_retrieval_service: PolicyRetrievalService | None = None) -> None:
        self.policy_retrieval_service = policy_retrieval_service or PolicyRetrievalService()

    def run(self, query: str, top_k: int = 5) -> tuple[dict[str, Any], str]:
        references = self.policy_retrieval_service.search(query, top_k=top_k)
        serialized_references = [reference.model_dump() for reference in references]
        return {
            "policy_references": serialized_references,
        }, f"Retrieved {len(serialized_references)} policy references"
