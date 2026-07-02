import os

from app.core.config import settings
from app.services.llm.mock_llm_client import MockLLMClient
from app.services.llm.openai_compatible_client import LLMClientError, OpenAICompatibleLLMClient


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def create_llm_client():
    provider = os.getenv("LLM_PROVIDER", settings.llm_provider).strip().lower()
    if provider == "mock":
        return MockLLMClient()

    if provider == "dashscope":
        real_api_enabled = _env_bool("LLM_ENABLE_REAL_API", settings.llm_enable_real_api)
        api_key = os.getenv("DASHSCOPE_API_KEY", settings.dashscope_api_key or "")
        base_url = os.getenv("DASHSCOPE_BASE_URL", settings.dashscope_base_url)
        model = os.getenv("DASHSCOPE_MODEL", settings.dashscope_model)
        timeout = int(os.getenv("LLM_TIMEOUT_SECONDS", str(settings.llm_timeout_seconds)))
        if not real_api_enabled or not api_key:
            return MockLLMClient()
        try:
            return OpenAICompatibleLLMClient(
                api_key=api_key,
                base_url=base_url,
                model=model,
                timeout_seconds=timeout,
            )
        except LLMClientError:
            return MockLLMClient()

    return MockLLMClient()


def current_llm_provider_name() -> str:
    provider = os.getenv("LLM_PROVIDER", settings.llm_provider).strip().lower()
    if provider == "dashscope" and not _env_bool("LLM_ENABLE_REAL_API", settings.llm_enable_real_api):
        return "mock"
    return provider if provider in {"mock", "dashscope"} else "mock"
