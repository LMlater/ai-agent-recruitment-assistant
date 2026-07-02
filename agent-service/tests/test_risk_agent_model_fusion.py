from app.agents.risk import RiskAgent
from app.schemas.review import ReviewRequest


class FakeRiskModelService:
    def __init__(self, probability=0.58, label="MEDIUM", raises=None):
        self.probability = probability
        self.label = label
        self.raises = raises
        self.last_features = None

    def predict_risk(self, features):
        self.last_features = features
        if self.raises:
            raise self.raises
        return {
            "model_risk_probability": self.probability,
            "model_risk_label": self.label,
            "model_version": "logistic_regression_baseline",
            "features_used": list(features.keys()),
            "explanation": ["fake model explanation"],
        }


def _state(**overrides):
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
    return {"request": ReviewRequest(**payload), "agent_results": []}


def test_risk_agent_combines_rule_score_and_model_signal():
    model_service = FakeRiskModelService(probability=0.58, label="MEDIUM")
    updates, _, output_summary = RiskAgent(risk_model_service=model_service).process(_state())
    assessment = updates["risk_assessment"]

    assert assessment["model_used"] is True
    assert assessment["model_risk_probability"] == 0.58
    assert assessment["model_risk_level"] == "MEDIUM"
    assert assessment["rule_score"] == 100
    assert assessment["rule_level"] == "LOW"
    assert assessment["risk_score"] == 80
    assert assessment["risk_level"] == "MEDIUM"
    assert updates["risk_score"] == 80
    assert updates["risk_level"] == "MEDIUM"
    assert model_service.last_features["debt_income_ratio"] == assessment["debt_income_ratio"]
    assert "model signal" in output_summary


def test_risk_agent_upgrades_to_high_when_model_is_high_risk():
    model_service = FakeRiskModelService(probability=0.82, label="HIGH")
    updates, _, _ = RiskAgent(risk_model_service=model_service).process(_state())
    assessment = updates["risk_assessment"]

    assert assessment["rule_level"] == "LOW"
    assert assessment["model_risk_level"] == "HIGH"
    assert assessment["risk_level"] == "HIGH"
    assert assessment["suggested_amount"] == 72000


def test_risk_agent_falls_back_to_rule_scoring_when_model_unavailable():
    model_service = FakeRiskModelService(raises=RuntimeError("model unavailable"))
    state = _state()

    new_state = RiskAgent(risk_model_service=model_service).run(state)
    assessment = new_state["risk_assessment"]

    assert assessment["model_used"] is False
    assert assessment["model_error"]
    assert assessment["risk_score"] == assessment["rule_score"]
    assert assessment["risk_level"] == assessment["rule_level"]
    assert new_state["agent_results"][-1].status == "SUCCESS"
    assert "fallback" in new_state["agent_results"][-1].output_summary.lower()
