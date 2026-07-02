import sys
from types import SimpleNamespace

import pytest

from app.services.llm.openai_compatible_client import LLMClientError, OpenAICompatibleLLMClient


def test_openai_compatible_client_uses_configured_model_base_url_and_api_key(monkeypatch):
    captured = {}

    class FakeCompletions:
        def create(self, **kwargs):
            captured["request"] = kwargs
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(message=SimpleNamespace(content="mock provider response"))
                ]
            )

    class FakeOpenAI:
        def __init__(self, **kwargs):
            captured["client"] = kwargs
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))

    client = OpenAICompatibleLLMClient(
        api_key="test-secret-key",
        base_url="https://dashscope.example.com/compatible-mode/v1",
        model="qwen-plus",
        timeout_seconds=7,
    )
    result = client.generate([{"role": "user", "content": "hello"}], temperature=0.3, max_tokens=99)

    assert result == "mock provider response"
    assert captured["client"]["api_key"] == "test-secret-key"
    assert captured["client"]["base_url"] == "https://dashscope.example.com/compatible-mode/v1"
    assert captured["client"]["timeout"] == 7
    assert captured["request"]["model"] == "qwen-plus"
    assert captured["request"]["messages"] == [{"role": "user", "content": "hello"}]
    assert captured["request"]["temperature"] == 0.3
    assert captured["request"]["max_tokens"] == 99


def test_openai_compatible_client_sanitizes_api_key_from_errors(monkeypatch):
    class FakeCompletions:
        def create(self, **kwargs):
            raise RuntimeError("request failed with test-secret-key")

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=FakeOpenAI))
    client = OpenAICompatibleLLMClient(
        api_key="test-secret-key",
        base_url="https://dashscope.example.com/compatible-mode/v1",
        model="qwen-plus",
    )

    with pytest.raises(LLMClientError) as exc_info:
        client.generate([{"role": "user", "content": "hello"}])

    assert "test-secret-key" not in str(exc_info.value)
    assert "request failed" in str(exc_info.value)
