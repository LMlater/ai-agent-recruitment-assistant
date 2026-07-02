import os

from app.services.llm.llm_client_factory import create_llm_client
from app.services.llm.mock_llm_client import MockLLMClient


def test_regular_tests_force_mock_llm_provider():
    assert os.getenv("LLM_PROVIDER") == "mock"
    assert os.getenv("LLM_ENABLE_REAL_API") == "false"
    assert os.getenv("DASHSCOPE_API_KEY") == ""
    assert os.getenv("DASHSCOPE_BASE_URL") == ""
    assert isinstance(create_llm_client(), MockLLMClient)
