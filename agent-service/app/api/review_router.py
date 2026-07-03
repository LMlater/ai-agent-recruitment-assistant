import os

from fastapi import APIRouter

from app.core.config import _env_bool, settings
from app.schemas.review import ReviewRequest, ReviewResponse
from app.workflow.review_workflow import ReviewWorkflow


router = APIRouter(prefix="/api/v1", tags=["reviews"])
workflow = ReviewWorkflow()


@router.post("/reviews", response_model=ReviewResponse)
def create_review(request: ReviewRequest) -> ReviewResponse:
    return workflow.run(request)


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@router.get("/debug/llm-config")
def llm_config_debug() -> dict[str, object]:
    provider = os.getenv("LLM_PROVIDER", settings.llm_provider).strip().lower() or "mock"
    return {
        "llm_provider": provider,
        "llm_enable_real_api": _env_bool("LLM_ENABLE_REAL_API", settings.llm_enable_real_api),
        "dashscope_api_key_present": bool(os.getenv("DASHSCOPE_API_KEY", settings.dashscope_api_key or "").strip()),
        "llm_timeout_seconds": _env_int("LLM_TIMEOUT_SECONDS", settings.llm_timeout_seconds),
        "llm_max_tokens": _env_int("LLM_MAX_TOKENS", settings.llm_max_tokens),
    }
