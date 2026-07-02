from pathlib import Path
import os

from pydantic import BaseModel


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class Settings(BaseModel):
    app_name: str = "SmartCreditMultiAgent Agent Service"
    knowledge_base_dir: Path = Path(__file__).resolve().parents[2] / "knowledge_base"
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock")
    llm_enable_real_api: bool = _env_bool("LLM_ENABLE_REAL_API", False)
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    dashscope_base_url: str = os.getenv(
        "DASHSCOPE_BASE_URL",
        "https://replace-with-your-bailian-compatible-mode-base-url/v1",
    )
    dashscope_model: str = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
    llm_timeout_seconds: int = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "1200"))


settings = Settings()
