import pytest

from scripts.evaluate_policy_retrieval import compute_metrics, evaluate_policy_retrieval, load_questions


def test_compute_metrics_from_expected_and_retrieved_policy_codes():
    evaluated_cases = [
        {
            "expected_policy_codes": ["R-001", "R-002"],
            "retrieved_policy_codes": ["R-001", "C-001", "R-002"],
        },
        {
            "expected_policy_codes": ["M-002"],
            "retrieved_policy_codes": ["P-001", "M-002"],
        },
        {
            "expected_policy_codes": ["C-001"],
            "retrieved_policy_codes": ["R-001"],
        },
    ]

    metrics = compute_metrics(evaluated_cases)

    assert metrics["case_count"] == 3
    assert metrics["recall_at_3"] == pytest.approx(2 / 3)
    assert metrics["recall_at_5"] == pytest.approx(2 / 3)
    assert metrics["hit_rate"] == pytest.approx(2 / 3)
    assert metrics["mrr"] == pytest.approx(0.5)


def test_rag_questions_include_expected_documents():
    questions = load_questions()

    assert questions
    assert all(question["expected_documents"] for question in questions)
    assert "risk_control_policy.md" in {
        document
        for question in questions
        for document in question["expected_documents"]
    }


def test_evaluation_output_uses_relative_metadata_paths_and_keeps_expected_documents():
    result = evaluate_policy_retrieval(top_k=1)
    metadata = result["metadata"]

    assert metadata["knowledge_base_dir"] == "agent-service/knowledge_base"
    assert metadata["questions_path"] == "data/eval/rag_questions.jsonl"
    assert "D:" not in metadata["knowledge_base_dir"]
    assert "D:" not in metadata["questions_path"]
    assert result["cases"][0]["expected_documents"]
