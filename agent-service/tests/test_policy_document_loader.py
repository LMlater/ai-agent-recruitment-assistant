import shutil
from pathlib import Path
from uuid import uuid4

import pytest

from app.services.policy_document_loader import PolicyDocumentLoader


@pytest.fixture
def knowledge_base_dir():
    base_dir = Path(__file__).resolve().parents[1] / "pytest-cache-files-policy-loader" / uuid4().hex
    base_dir.mkdir(parents=True)
    try:
        yield base_dir
    finally:
        shutil.rmtree(base_dir, ignore_errors=True)
        try:
            base_dir.parent.rmdir()
        except OSError:
            pass


def test_loads_markdown_policy_sections_with_stable_metadata(knowledge_base_dir):
    (knowledge_base_dir / "risk_control_policy.md").write_text(
        """# Mock Risk Control Policy

## R-001 Debt-to-Income Ratio

Debt-to-income ratio above 80% requires high-risk manual review.

## R-002 Overdue Records

More overdue records should reduce the mock score.
""",
        encoding="utf-8",
    )

    chunks = PolicyDocumentLoader(knowledge_base_dir).load_chunks()

    assert [chunk.policy_code for chunk in chunks] == ["R-001", "R-002"]
    assert chunks[0].chunk_id == "risk_control_policy.md::R-001"
    assert chunks[0].document_name == "risk_control_policy.md"
    assert chunks[0].section_title == "R-001 Debt-to-Income Ratio"
    assert "above 80%" in chunks[0].text


def test_generates_stable_chunk_id_when_section_has_no_policy_code(knowledge_base_dir):
    (knowledge_base_dir / "material_review_policy.md").write_text(
        """# Mock Material Review Policy

## Missing Income Proof

Missing income proof requires supplementary material review.
""",
        encoding="utf-8",
    )

    chunks = PolicyDocumentLoader(knowledge_base_dir).load_chunks()

    assert len(chunks) == 1
    assert chunks[0].policy_code is None
    assert chunks[0].chunk_id == "material_review_policy.md::missing-income-proof"


def test_empty_directory_returns_no_chunks(knowledge_base_dir):
    chunks = PolicyDocumentLoader(knowledge_base_dir).load_chunks()

    assert chunks == []
