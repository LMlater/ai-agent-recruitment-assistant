from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.review_router import router as review_router


app = FastAPI(
    title="SmartCreditMultiAgent Agent Service",
    description="FastAPI + LangGraph multi-agent credit review service.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(review_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
