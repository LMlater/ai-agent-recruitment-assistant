from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _payload(**overrides):
    payload = {
        "application_id": 1,
        "customer": {
            "id": 1,
            "age": 32,
            "monthly_income": 12000,
            "work_years": 5,
            "existing_debt": 30000,
            "overdue_count": 0,
            "asset_proof_count": 2,
        },
        "loan_application": {
            "amount": 80000,
            "term_months": 24,
            "purpose": "personal consumption",
        },
    }
    payload["customer"].update(overrides.pop("customer", {}))
    payload["loan_application"].update(overrides.pop("loan_application", {}))
    payload.update(overrides)
    return payload


def _post_review(payload):
    response = client.post("/api/v1/reviews", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["workflow_id"]
    assert body["final_decision"]
    assert body["agent_results"]
    assert body["report"]
    assert {item["agent_name"] for item in body["agent_results"]} == {
        "IntakeAgent",
        "RiskAgent",
        "PolicyAgent",
        "ComplianceAgent",
        "DecisionAgent",
    }
    for item in body["agent_results"]:
        assert item["status"] == "SUCCESS"
        assert item["started_at"]
        assert item["ended_at"]
        assert item["duration_ms"] >= 0
    return body


def test_low_risk_review():
    body = _post_review(_payload())

    assert body["risk_level"] == "LOW"
    assert body["risk_score"] >= 80
    assert body["final_decision"] == "APPROVE"
    assert body["suggested_amount"] == 80000
    assert body["report"]["risk_assessment"]["risk_level"] == "LOW"


def test_medium_risk_review():
    body = _post_review(
        _payload(
            customer={
                "monthly_income": 9000,
                "work_years": 2,
                "existing_debt": 65000,
                "overdue_count": 1,
                "asset_proof_count": 1,
            },
            loan_application={"amount": 130000},
        )
    )

    assert body["risk_level"] == "MEDIUM"
    assert 60 <= body["risk_score"] < 80
    assert body["final_decision"] in {"NEED_MORE_INFO", "REVIEW"}


def test_high_risk_review():
    body = _post_review(
        _payload(
            customer={
                "monthly_income": 5000,
                "work_years": 0,
                "existing_debt": 140000,
                "overdue_count": 4,
                "asset_proof_count": 0,
            },
            loan_application={"amount": 160000},
        )
    )

    assert body["risk_level"] == "HIGH"
    assert body["risk_score"] < 60
    assert body["final_decision"] == "REJECT"
    assert body["suggested_amount"] < 160000
    assert any("manual" in warning.lower() or "人工" in warning for warning in body["report"]["compliance_warnings"])


def test_missing_material_review():
    body = _post_review(
        _payload(
            customer={
                "age": 17,
                "monthly_income": 0,
                "asset_proof_count": 0,
            }
        )
    )

    assert body["final_decision"] == "NEED_MORE_INFO"
    assert body["report"]["intake_check"]["complete"] is False
    assert body["report"]["required_materials"]


def test_agent_results_contains_all_agents():
    body = _post_review(_payload())

    assert [item["agent_name"] for item in body["agent_results"]] == [
        "IntakeAgent",
        "RiskAgent",
        "PolicyAgent",
        "ComplianceAgent",
        "DecisionAgent",
    ]
