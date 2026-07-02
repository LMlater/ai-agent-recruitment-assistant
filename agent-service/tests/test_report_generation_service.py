from app.services.report_generation_service import ReportGenerationService


class JsonLLMClient:
    def generate(self, messages, temperature=0.2, max_tokens=1200):
        self.messages = messages
        return '{"summary":"LLM summary cites R-001 and asks for manual review.","decision_reasons":["Rule reason retained.","Policy R-001 retained.","AI/ML only assist final manual approval."]}'


class PlainTextLLMClient:
    def generate(self, messages, temperature=0.2, max_tokens=1200):
        return "not json"


class FailingLLMClient:
    def generate(self, messages, temperature=0.2, max_tokens=1200):
        raise RuntimeError("provider failed")


def _context():
    return {
        "final_decision": "NEED_MORE_INFO",
        "risk_level": "MEDIUM",
        "risk_score": 68,
        "suggested_amount": 90000,
        "summary": "base deterministic summary",
        "decision_reasons": ["Debt-to-income ratio is above 60%."],
        "risk_assessment": {
            "rule_reasons": ["Debt-to-income ratio is above 60%."],
            "model_used": True,
            "model_risk_probability": 0.58,
            "model_risk_level": "MEDIUM",
        },
        "policy_references": [
            {
                "policy_code": "R-001",
                "document_name": "risk_control_policy.md",
                "section_title": "R-001 Debt-to-Income Ratio Control",
                "content": "Debt-to-income ratio requires manual review.",
                "score": 0.82,
            }
        ],
        "compliance_warnings": ["AI output is approval assistance only."],
        "required_materials": ["Valid income proof is required."],
    }


def test_report_generation_service_parses_json_llm_response():
    client = JsonLLMClient()
    service = ReportGenerationService(llm_client=client, llm_provider="mock")

    result = service.generate(_context())

    assert result["llm_used"] is True
    assert result["llm_provider"] == "mock"
    assert result["llm_error"] is None
    assert result["summary"] == "LLM summary cites R-001 and asks for manual review."
    assert "Policy R-001 retained." in result["decision_reasons"]
    assert "R-001" in client.messages[-1]["content"]


def test_report_generation_service_falls_back_when_llm_returns_non_json():
    service = ReportGenerationService(llm_client=PlainTextLLMClient(), llm_provider="mock")

    result = service.generate(_context())

    assert result["llm_used"] is False
    assert "R-001" in " ".join(result["decision_reasons"])
    assert "人工审批" in result["summary"] or "人工复核" in result["summary"]


def test_report_generation_service_falls_back_when_llm_raises():
    service = ReportGenerationService(llm_client=FailingLLMClient(), llm_provider="mock")

    result = service.generate(_context())

    assert result["llm_used"] is False
    assert result["llm_error"] == "provider failed"
    assert "R-001" in " ".join(result["decision_reasons"])
    assert "人工审批" in result["summary"] or "人工复核" in result["summary"]
