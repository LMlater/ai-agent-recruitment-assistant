import json

from app.services.llm.prompt_templates import build_report_messages


def _payload_from_messages(messages):
    user_content = messages[-1]["content"]
    return json.loads(user_content[user_content.index("{") :])


def test_report_prompt_compacts_policy_references_and_risk_assessment():
    long_content = "A" * 300
    messages = build_report_messages(
        {
            "final_decision": "NEED_MORE_INFO",
            "risk_level": "MEDIUM",
            "risk_score": 68,
            "suggested_amount": 90000,
            "summary": "Base summary",
            "decision_reasons": ["Base reason"],
            "risk_assessment": {
                "risk_score": 68,
                "risk_level": "MEDIUM",
                "rule_reasons": ["Debt-to-income ratio is high."],
                "model_used": True,
                "model_risk_probability": 0.42,
                "model_risk_level": "MEDIUM",
                "model_version": "test-model",
                "fusion_strategy": "max-risk",
                "raw_features": {"should": "not be sent"},
                "very_long_internal_detail": "B" * 300,
            },
            "policy_references": [
                {
                    "policy_code": "R-001",
                    "document_name": "risk_control_policy.md",
                    "section_title": "Debt-to-Income Ratio Control",
                    "content": long_content,
                    "score": 0.88,
                }
            ],
        }
    )

    payload = _payload_from_messages(messages)

    assert payload["allowed_policy_codes"] == ["R-001"]
    assert payload["policy_references"] == [
        {
            "policy_code": "R-001",
            "section_title": "Debt-to-Income Ratio Control",
            "content": ("A" * 117) + "...",
        }
    ]
    assert len(payload["policy_references"][0]["content"]) == 120
    assert payload["risk_assessment"] == {
        "risk_score": 68,
        "risk_level": "MEDIUM",
        "rule_reasons": ["Debt-to-income ratio is high."],
        "model_used": True,
        "model_risk_probability": 0.42,
        "model_risk_level": "MEDIUM",
        "model_version": "test-model",
        "fusion_strategy": "max-risk",
    }
    assert "raw_features" not in json.dumps(payload, ensure_ascii=False)


def test_report_prompt_keeps_policy_code_guardrail():
    messages = build_report_messages({"policy_references": [{"policy_code": "C-001", "content": "short"}]})
    user_content = messages[-1]["content"]

    assert "allowed_policy_codes" in user_content
    assert "C-001" in user_content
