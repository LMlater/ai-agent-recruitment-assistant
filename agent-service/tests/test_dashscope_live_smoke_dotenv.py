import importlib.util
import os
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_smoke_module(module_name: str):
    module_path = Path(__file__).resolve().parent / "test_dashscope_live_smoke.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_dashscope_smoke_module_loads_dotenv_before_skipif(monkeypatch):
    loaded = {}

    def fake_load_dotenv(path, override=False):
        loaded["path"] = Path(path)
        loaded["override"] = override
        if override or "DASHSCOPE_API_KEY" not in os.environ:
            monkeypatch.setenv("DASHSCOPE_API_KEY", "fake-api-key")
        if override or "DASHSCOPE_BASE_URL" not in os.environ:
            monkeypatch.setenv("DASHSCOPE_BASE_URL", "https://fake.example/v1")
        if override or "LLM_ENABLE_REAL_API" not in os.environ:
            monkeypatch.setenv("LLM_ENABLE_REAL_API", "true")

    monkeypatch.setitem(sys.modules, "dotenv", SimpleNamespace(load_dotenv=fake_load_dotenv))
    monkeypatch.delenv("SMARTCREDIT_FORCE_MOCK_LLM_TESTS", raising=False)
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.delenv("DASHSCOPE_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_ENABLE_REAL_API", raising=False)

    module = _load_smoke_module("dashscope_smoke_dotenv_enabled")

    assert loaded["path"].name == ".env"
    assert loaded["path"].parent.name == "agent-service"
    assert loaded["override"] is False
    assert module._dashscope_smoke_disabled() is False


def test_dashscope_smoke_remains_disabled_without_required_env(monkeypatch):
    calls = []

    def fake_load_dotenv(path, override=False):
        calls.append((Path(path), override))

    class FailingClient:
        def __init__(self, *args, **kwargs):
            raise AssertionError("Live client should not be constructed when smoke test is disabled.")

    monkeypatch.setitem(sys.modules, "dotenv", SimpleNamespace(load_dotenv=fake_load_dotenv))
    monkeypatch.delenv("SMARTCREDIT_FORCE_MOCK_LLM_TESTS", raising=False)
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.delenv("DASHSCOPE_BASE_URL", raising=False)
    monkeypatch.setenv("LLM_ENABLE_REAL_API", "false")

    module = _load_smoke_module("dashscope_smoke_dotenv_disabled")
    monkeypatch.setattr(module, "OpenAICompatibleLLMClient", FailingClient)

    assert calls
    assert module._dashscope_smoke_disabled() is True
