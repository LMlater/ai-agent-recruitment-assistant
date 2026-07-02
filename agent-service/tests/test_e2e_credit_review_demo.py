import importlib.util
from pathlib import Path


def _load_demo_module():
    module_path = Path(__file__).resolve().parents[2] / "scripts" / "run_e2e_credit_review_demo.py"
    spec = importlib.util.spec_from_file_location("run_e2e_credit_review_demo", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_e2e_demo_summary_extracts_ai_report_logs_and_llm_provider():
    module = _load_demo_module()

    summary = module.build_demo_summary(
        application_id=7,
        ai_review_response={
            "workflow_id": "workflow-7",
            "final_decision": "NEED_MORE_INFO",
            "risk_level": "MEDIUM",
            "risk_score": 78,
            "suggested_amount": 90000,
            "agent_results": [
                {
                    "agent_name": "DecisionAgent",
                    "result": {
                        "decision_report_generation": {
                            "llm_used": True,
                            "llm_provider": "mock",
                            "llm_error": None,
                        }
                    },
                }
            ],
            "report": {
                "policy_references": [
                    {"policy_code": "R-001"},
                    {"policy_code": "P-003"},
                ]
            },
        },
        reports=[{"id": 12, "reportJson": "{}"}],
        logs=[
            {"agentName": "IntakeAgent"},
            {"agentName": "DecisionAgent", "outputSummary": "llm_provider=mock; llm_used=true"},
        ],
    )

    assert summary == {
        "application_id": 7,
        "ai_review_triggered": True,
        "workflow_id": "workflow-7",
        "final_decision_from_ai": "NEED_MORE_INFO",
        "risk_level": "MEDIUM",
        "risk_score": 78,
        "suggested_amount": 90000,
        "ai_report_id": 12,
        "agent_log_count": 2,
        "decision_agent_llm_provider": "mock",
        "policy_codes": ["R-001", "P-003"],
        "manual_approval_required": True,
    }


def test_e2e_demo_summary_includes_optional_manual_decision_status():
    module = _load_demo_module()

    summary = module.build_demo_summary(
        application_id=8,
        ai_review_response={
            "workflow_id": "workflow-8",
            "final_decision": "APPROVE",
            "risk_level": "LOW",
            "risk_score": 92,
            "suggested_amount": 80000,
            "agent_results": [],
            "report": {"policy_references": []},
        },
        reports=[],
        logs=[],
        manual_decision_response={"toStatus": "APPROVED"},
    )

    assert summary["manual_decision_applied"] is True
    assert summary["manual_decision_status"] == "APPROVED"
