from fastapi import FastAPI

from app.api.review_router import router as review_router


app = FastAPI(
    title="SmartCreditMultiAgent Agent Service",
    description="FastAPI + LangGraph multi-agent credit review service.",
    version="0.1.0",
)

app.include_router(review_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
