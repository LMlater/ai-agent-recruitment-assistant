import shutil
from pathlib import Path
from uuid import uuid4

import pytest

from app.services.policy_retrieval_service import PolicyRetrievalService


@pytest.fixture
def knowledge_base_dir():
    base_dir = Path(__file__).resolve().parents[1] / "pytest-cache-files-policy-retrieval" / uuid4().hex
    base_dir.mkdir(parents=True)
    try:
        yield base_dir
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)
        try:
            base_dir.parent.rmdir()
        except OSError:
            pass


def _write_policy_docs(knowledge_base_dir):
    (knowledge_base_dir / "risk_control_policy.md").write_text(
        """# Mock Risk Control Policy

## R-001 Debt-to-Income Ratio

Debt-to-income ratio above 80% requires high-risk manual review.

## R-002 Overdue Records

Customers with multiple overdue records must be treated as elevated credit risk.
""",
        encoding="utf-8",
    )
    (knowledge_base_dir / "compliance_review_policy.md").write_text(
        """# Mock Compliance Review Policy

## C-001 AI Assistance Boundary

AI and ML model output can only be used as approval assistance. It cannot automatically approve.
""",
        encoding="utf-8",
    )


def test_search_returns_sorted_structured_policy_references(knowledge_base_dir):
    _write_policy_docs(knowledge_base_dir)
    service = PolicyRetrievalService(knowledge_base_dir=knowledge_base_dir)

    results = service.search("high debt income ratio manual review", top_k=2)

    assert [result.policy_code for result in results] == ["R-001", "R-002"]
    assert results[0].document_name == "risk_control_policy.md"
    assert results[0].section_title == "R-001 Debt-to-Income Ratio"
    assert "manual review" in results[0].content
    assert results[0].score >= results[1].score > 0


def test_search_finds_ai_auto_approval_boundary(knowledge_base_dir):
    _write_policy_docs(knowledge_base_dir)
    service = PolicyRetrievalService(knowledge_base_dir=knowledge_base_dir)

    results = service.search("AI must not automatically approve by model", top_k=1)

    assert len(results) == 1
    assert results[0].policy_code == "C-001"
    assert "cannot automatically approve" in results[0].content


def test_blank_or_unmatched_query_returns_empty_list(knowledge_base_dir):
    _write_policy_docs(knowledge_base_dir)
    service = PolicyRetrievalService(knowledge_base_dir=knowledge_base_dir)

    assert service.search("", top_k=3) == []
    assert service.search("zzzz qqqq xxxx", top_k=3) == []
