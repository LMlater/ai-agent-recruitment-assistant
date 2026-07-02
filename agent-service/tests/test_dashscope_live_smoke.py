import os
from pathlib import Path

import pytest

from app.services.llm.openai_compatible_client import OpenAICompatibleLLMClient


def _load_local_env():
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(env_path, override=False)


def _dashscope_smoke_disabled() -> bool:
    return (
        not os.getenv("DASHSCOPE_API_KEY")
        or not os.getenv("DASHSCOPE_BASE_URL")
        or os.getenv("LLM_ENABLE_REAL_API") != "true"
    )


_load_local_env()


@pytest.mark.integration
@pytest.mark.skipif(
    _dashscope_smoke_disabled(),
    reason="DashScope live smoke test requires local API key, base URL, and explicit enable flag",
)
def test_dashscope_live_smoke():
    client = OpenAICompatibleLLMClient(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_BASE_URL"),
        model=os.getenv("DASHSCOPE_MODEL", "qwen-plus"),
        timeout_seconds=10,
    )

    result = client.generate([{"role": "user", "content": "Reply with OK."}], max_tokens=8)

    assert result
