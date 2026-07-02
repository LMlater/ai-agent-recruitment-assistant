from app.agents.decision import DecisionAgent


def test_decision_agent_includes_ml_model_signal_when_available():
    updates, _, _ = DecisionAgent().process(
        {
            "risk_level": "MEDIUM",
            "required_materials": [],
            "risk_assessment": {
                "rule_reasons": ["Debt-to-income ratio is above 40%."],
                "model_used": True,
                "model_risk_probability": 0.58,
                "model_risk_level": "MEDIUM",
                "model_version": "logistic_regression_baseline",
            },
        }
    )

    reasons = updates["decision_reasons"]
    assert any("probability=0.58" in reason for reason in reasons)
    assert any("level=MEDIUM" in reason for reason in reasons)
    assert any("version=logistic_regression_baseline" in reason for reason in reasons)
    assert any("final approval must remain manual" in reason for reason in reasons)


def test_decision_agent_includes_rule_fallback_when_model_unavailable():
    updates, _, _ = DecisionAgent().process(
        {
            "risk_level": "LOW",
            "required_materials": [],
            "risk_assessment": {
                "rule_reasons": ["Rule score is stable."],
                "model_used": False,
                "model_error": "Risk model artifact not found",
            },
        }
    )

    assert any("rule scoring fallback" in reason for reason in updates["decision_reasons"])
