import os
import sys
from pathlib import Path

import pytest


FORCE_MOCK_ENV = "SMARTCREDIT_FORCE_MOCK_LLM_TESTS"


def _is_dashscope_smoke_only_run(argv: list[str] | None = None) -> bool:
    args = argv if argv is not None else sys.argv[1:]
    targets = [arg.split("::", 1)[0] for arg in args if not arg.startswith("-")]
    if not targets:
        return False
    return all(Path(target).name == "test_dashscope_live_smoke.py" for target in targets)


def _force_mock_llm_environment() -> None:
    os.environ[FORCE_MOCK_ENV] = "true"
    os.environ["LLM_PROVIDER"] = "mock"
    os.environ["LLM_ENABLE_REAL_API"] = "false"
    os.environ["DASHSCOPE_API_KEY"] = ""
    os.environ["DASHSCOPE_BASE_URL"] = ""


if not _is_dashscope_smoke_only_run():
    _force_mock_llm_environment()


@pytest.fixture(autouse=True)
def isolate_llm_provider_for_regular_tests(monkeypatch, request):
    if Path(str(request.fspath)).name == "test_dashscope_live_smoke.py" and _is_dashscope_smoke_only_run():
        return

    monkeypatch.setenv(FORCE_MOCK_ENV, "true")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_ENABLE_REAL_API", "false")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "")
    monkeypatch.setenv("DASHSCOPE_BASE_URL", "")
