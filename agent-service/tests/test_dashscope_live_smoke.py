import os

import pytest

from app.services.llm.openai_compatible_client import OpenAICompatibleLLMClient


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("DASHSCOPE_API_KEY") or os.getenv("LLM_ENABLE_REAL_API") != "true",
    reason="DashScope live smoke test requires local API key and explicit enable flag",
)
def test_dashscope_live_smoke():
    client = OpenAICompatibleLLMClient(
        api_key=os.environ["DASHSCOPE_API_KEY"],
        base_url=os.environ["DASHSCOPE_BASE_URL"],
        model=os.getenv("DASHSCOPE_MODEL", "qwen-plus"),
        timeout_seconds=10,
    )

    result = client.generate([{"role": "user", "content": "Reply with OK."}], max_tokens=8)

    assert result
