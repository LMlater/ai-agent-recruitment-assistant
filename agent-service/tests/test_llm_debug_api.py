from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_llm_debug_config_exists_and_uses_safe_fields(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "dashscope")
    monkeypatch.setenv("LLM_ENABLE_REAL_API", "true")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "secret-test-key")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "90")
    monkeypatch.setenv("LLM_MAX_TOKENS", "600")

    response = client.get("/api/v1/debug/llm-config")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "llm_provider": "dashscope",
        "llm_enable_real_api": True,
        "dashscope_api_key_present": True,
        "llm_timeout_seconds": 90,
        "llm_max_tokens": 600,
    }
    assert "secret-test-key" not in response.text


def test_llm_debug_config_key_presence_is_boolean(monkeypatch):
    monkeypatch.setenv("DASHSCOPE_API_KEY", "")

    response = client.get("/api/v1/debug/llm-config")

    assert response.status_code == 200
    assert response.json()["dashscope_api_key_present"] is False
    assert isinstance(response.json()["dashscope_api_key_present"], bool)
