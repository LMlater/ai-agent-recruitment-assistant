import importlib
import os
import sys
from pathlib import Path
from types import SimpleNamespace


def test_config_loads_agent_service_dotenv_without_overriding_existing_env(monkeypatch):
    loaded = {}

    def fake_load_dotenv(path, override=False):
        loaded["path"] = Path(path)
        loaded["override"] = override
        if override or "LLM_PROVIDER" not in os.environ:
            monkeypatch.setenv("LLM_PROVIDER", "dashscope")
        if override or "DASHSCOPE_MODEL" not in os.environ:
            monkeypatch.setenv("DASHSCOPE_MODEL", "qwen-plus-from-dotenv")

    monkeypatch.setitem(sys.modules, "dotenv", SimpleNamespace(load_dotenv=fake_load_dotenv))
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("DASHSCOPE_MODEL", "model-from-shell")

    import app.core.config as config

    reloaded = importlib.reload(config)

    assert loaded["path"].name == ".env"
    assert loaded["path"].parent.name == "agent-service"
    assert loaded["override"] is False
    assert reloaded.settings.llm_provider == "dashscope"
    assert reloaded.settings.dashscope_model == "model-from-shell"

    reloaded.settings.llm_provider = "mock"
    reloaded.settings.llm_enable_real_api = False
