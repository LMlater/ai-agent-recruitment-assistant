import pytest

from scripts.evaluate_policy_retrieval import compute_metrics


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
