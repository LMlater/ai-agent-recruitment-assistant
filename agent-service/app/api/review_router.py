from fastapi import APIRouter

from app.schemas.review import ReviewRequest, ReviewResponse
from app.workflow.review_workflow import ReviewWorkflow


router = APIRouter(prefix="/api/v1", tags=["reviews"])
workflow = ReviewWorkflow()


@router.post("/reviews", response_model=ReviewResponse)
def create_review(request: ReviewRequest) -> ReviewResponse:
    return workflow.run(request)
