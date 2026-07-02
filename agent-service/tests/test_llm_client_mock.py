from app.services.llm.llm_client_factory import create_llm_client
from app.services.llm.mock_llm_client import MockLLMClient


def test_mock_llm_client_returns_stable_manual_review_report_without_api_key(monkeypatch):
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    client = MockLLMClient()

    result = client.generate(
        [
            {"role": "system", "content": "You are a report generator."},
            {
                "role": "user",
                "content": "risk_level=MEDIUM; policy_codes=R-001,C-001; AI and ML are auxiliary.",
            },
        ]
    )

    assert result == client.generate([{"role": "user", "content": "risk_level=MEDIUM; policy_codes=R-001,C-001"}])
    assert "人工复核" in result
    assert "AI" in result
    assert "辅助" in result
    assert "R-001" in result


def test_unknown_llm_provider_falls_back_to_mock(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "unknown-provider")

    client = create_llm_client()

    assert isinstance(client, MockLLMClient)
