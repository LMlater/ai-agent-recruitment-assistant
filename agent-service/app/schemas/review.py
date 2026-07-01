from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CustomerPayload(BaseModel):
    id: int
    age: int
    monthly_income: float
    work_years: float
    existing_debt: float
    overdue_count: int
    asset_proof_count: int


class LoanApplicationPayload(BaseModel):
    amount: float
    term_months: int
    purpose: str


class ReviewRequest(BaseModel):
    application_id: int
    customer: CustomerPayload
    loan_application: LoanApplicationPayload


class AgentResult(BaseModel):
    agent_name: str
    status: str
    input_summary: str
    output_summary: str
    error_message: str | None = None
    started_at: datetime
    ended_at: datetime
    duration_ms: int
    result: dict[str, Any] = Field(default_factory=dict)


class ReviewReport(BaseModel):
    intake_check: dict[str, Any] = Field(default_factory=dict)
    risk_assessment: dict[str, Any] = Field(default_factory=dict)
    policy_references: list[str] = Field(default_factory=list)
    compliance_warnings: list[str] = Field(default_factory=list)
    decision_reasons: list[str] = Field(default_factory=list)
    required_materials: list[str] = Field(default_factory=list)


class ReviewResponse(BaseModel):
    workflow_id: str
    final_decision: str
    risk_level: str
    risk_score: int
    suggested_amount: float
    summary: str
    agent_results: list[AgentResult]
    report: ReviewReport
