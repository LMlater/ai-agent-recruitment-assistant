from app.agents.decision import DecisionAgent


class SuccessfulReportGenerationService:
    def generate(self, context):
        self.context = context
        return {
            "summary": "LLM generated summary with R-001 and final manual review.",
            "decision_reasons": [
                "Debt-to-income ratio is above 60%.",
                "model_risk_probability=0.58 and model_risk_level=MEDIUM.",
                "Policy codes: R-001.",
                "AI/ML outputs are approval assistance only; final approval must remain manual.",
            ],
            "llm_used": True,
            "llm_provider": "mock",
            "llm_error": None,
        }


class BrokenReportGenerationService:
    def generate(self, context):
        raise RuntimeError("llm exploded")


def _state():
    return {
        "agent_results": [],
        "risk_level": "MEDIUM",
        "risk_score": 68,
        "suggested_amount": 90000,
        "required_materials": [],
        "risk_assessment": {
            "rule_reasons": ["Debt-to-income ratio is above 60%."],
            "model_used": True,
            "model_risk_probability": 0.58,
            "model_risk_level": "MEDIUM",
            "model_version": "logistic_regression_baseline",
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
    }


def test_decision_agent_uses_llm_summary_without_changing_final_decision():
    service = SuccessfulReportGenerationService()
    updates, _, output_summary = DecisionAgent(report_generation_service=service).process(_state())

    assert updates["final_decision"] == "NEED_MORE_INFO"
    assert updates["summary"] == "LLM generated summary with R-001 and final manual review."
    assert "Policy codes: R-001." in updates["decision_reasons"]
    assert updates["decision_report_generation"]["llm_used"] is True
    assert service.context["final_decision"] == "NEED_MORE_INFO"
    assert "LLM" in output_summary


def test_decision_agent_falls_back_and_keeps_agent_success_when_llm_fails():
    state = _state()

    new_state = DecisionAgent(report_generation_service=BrokenReportGenerationService()).run(state)

    assert new_state["agent_results"][-1].status == "SUCCESS"
    assert new_state["final_decision"] == "NEED_MORE_INFO"
    assert new_state["summary"] == "申请人存在一定负债或额度压力，建议补充收入、资产或用途材料后由人工复核。"
    assert any("AI and ML outputs are approval assistance only" in reason for reason in new_state["decision_reasons"])
    assert new_state["decision_report_generation"]["llm_used"] is False
    assert "fallback" in new_state["agent_results"][-1].output_summary.lower()
