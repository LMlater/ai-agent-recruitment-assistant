import json
import os

from scripts.run_llm_review_demo import configure_demo_environment, run_demo_review


def test_llm_review_demo_returns_safe_mock_summary(monkeypatch):
    fake_key = "test-secret-demo-key"
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_ENABLE_REAL_API", "false")
    monkeypatch.setenv("DASHSCOPE_API_KEY", fake_key)

    result = run_demo_review(mode="mock")
    serialized = json.dumps(result, ensure_ascii=False)

    assert result["workflow_id"]
    assert result["final_decision"]
    assert result["risk_level"]
    assert isinstance(result["risk_score"], int)
    assert result["summary"]
    assert result["decision_reasons"]
    assert result["decision_report_generation"]
    assert result["decision_report_generation"]["llm_provider"] == "mock"
    assert result["demo_mode"] == "mock"
    assert result["llm_timeout_seconds"]
    assert result["llm_max_tokens"]
    assert result["policy_references"]
    assert all("policy_code" in item for item in result["policy_references"])
    assert fake_key not in serialized


def test_real_demo_mode_sets_stable_defaults_without_overriding_user_values(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_ENABLE_REAL_API", raising=False)
    monkeypatch.delenv("LLM_TIMEOUT_SECONDS", raising=False)
    monkeypatch.setenv("LLM_MAX_TOKENS", "777")

    warnings = configure_demo_environment("real", compact=False)

    assert warnings
    assert "DASHSCOPE_API_KEY" in warnings[0]
    assert "DASHSCOPE_BASE_URL" in warnings[0]
    assert os.environ["LLM_PROVIDER"] == "dashscope"
    assert os.environ["LLM_ENABLE_REAL_API"] == "true"
    assert os.environ["LLM_TIMEOUT_SECONDS"] == "90"
    assert os.environ["LLM_MAX_TOKENS"] == "777"


def test_compact_demo_mode_uses_smaller_generation_defaults(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_ENABLE_REAL_API", "false")
    monkeypatch.delenv("LLM_TIMEOUT_SECONDS", raising=False)
    monkeypatch.delenv("LLM_MAX_TOKENS", raising=False)

    result = run_demo_review(mode="env", compact=True)

    assert result["demo_mode"] == "env"
    assert result["llm_timeout_seconds"] == 90
    assert result["llm_max_tokens"] == 600
