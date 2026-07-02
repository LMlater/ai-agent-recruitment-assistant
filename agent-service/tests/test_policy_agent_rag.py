from app.agents.policy import PolicyAgent
from app.schemas.policy import PolicyReference
from app.schemas.review import ReviewRequest


class FakePolicyRetrievalService:
    def __init__(self):
        self.last_query = None
        self.last_top_k = None

    def search(self, query, top_k=5):
        self.last_query = query
        self.last_top_k = top_k
        return [
            PolicyReference(
                policy_code="R-001",
                document_name="risk_control_policy.md",
                section_title="R-001 Debt-to-Income Ratio",
                content="High debt-to-income ratio requires manual review.",
                score=0.42,
            )
        ]


def _state():
    return {
        "request": ReviewRequest(
            application_id=1,
            customer={
                "id": 1,
                "age": 32,
                "monthly_income": 9000,
                "work_years": 2,
                "existing_debt": 65000,
                "overdue_count": 1,
                "asset_proof_count": 0,
            },
            loan_application={
                "amount": 130000,
                "term_months": 24,
                "purpose": "personal consumption",
            },
        ),
        "risk_level": "MEDIUM",
        "risk_score": 68,
        "required_materials": ["Valid income proof is required."],
        "compliance_warnings": [
            "ML model output is an auxiliary signal and must be reviewed with policy references."
        ],
        "risk_assessment": {
            "rule_reasons": [
                "Debt-to-income ratio is above 60%.",
                "Requested amount is above 12 months of income.",
            ],
            "model_used": True,
            "model_risk_probability": 0.58,
            "model_risk_level": "MEDIUM",
            "model_version": "logistic_regression_baseline",
            "debt_income_ratio": 0.6019,
        },
    }


def test_policy_agent_builds_contextual_query_and_returns_structured_references():
    retrieval_service = FakePolicyRetrievalService()
    updates, input_summary, output_summary = PolicyAgent(policy_retrieval_service=retrieval_service).process(_state())

    assert retrieval_service.last_top_k == 5
    query = retrieval_service.last_query
    assert "personal consumption" in query
    assert "amount 130000" in query
    assert "MEDIUM" in query
    assert "Debt-to-income ratio is above 60%" in query
    assert "Valid income proof is required" in query
    assert "ML model auxiliary" in query
    assert "manual review" in query
    assert "AI cannot auto approve" in query
    assert updates["policy_references"] == [
        {
            "policy_code": "R-001",
            "document_name": "risk_control_policy.md",
            "section_title": "R-001 Debt-to-Income Ratio",
            "content": "High debt-to-income ratio requires manual review.",
            "score": 0.42,
        }
    ]
    assert "RAG" in input_summary
    assert output_summary == "Retrieved 1 policy references"
