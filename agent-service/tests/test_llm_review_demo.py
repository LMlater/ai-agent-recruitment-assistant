import json

from scripts.run_llm_review_demo import run_demo_review


def test_llm_review_demo_returns_safe_mock_summary(monkeypatch):
    fake_key = "test-secret-demo-key"
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_ENABLE_REAL_API", "false")
    monkeypatch.setenv("DASHSCOPE_API_KEY", fake_key)

    result = run_demo_review()
    serialized = json.dumps(result, ensure_ascii=False)

    assert result["workflow_id"]
    assert result["final_decision"]
    assert result["risk_level"]
    assert isinstance(result["risk_score"], int)
    assert result["summary"]
    assert result["decision_reasons"]
    assert result["decision_report_generation"]
    assert result["decision_report_generation"]["llm_provider"] == "mock"
    assert result["policy_references"]
    assert all("policy_code" in item for item in result["policy_references"])
    assert fake_key not in serialized
