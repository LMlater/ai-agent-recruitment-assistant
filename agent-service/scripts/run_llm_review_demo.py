from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.schemas.review import ReviewRequest
from app.workflow.review_workflow import ReviewWorkflow


def build_demo_request() -> ReviewRequest:
    return ReviewRequest(
        application_id=9001,
        customer={
            "id": 9001,
            "age": 34,
            "monthly_income": 9000,
            "work_years": 4,
            "existing_debt": 56000,
            "overdue_count": 1,
            "asset_proof_count": 1,
        },
        loan_application={
            "amount": 120000,
            "term_months": 24,
            "purpose": "small business cash flow",
        },
    )


def run_demo_review() -> dict[str, Any]:
    response = ReviewWorkflow().run(build_demo_request())
    decision_agent_result = next(
        (item for item in response.agent_results if item.agent_name == "DecisionAgent"),
        None,
    )
    decision_report_generation = {}
    if decision_agent_result:
        decision_report_generation = decision_agent_result.result.get("decision_report_generation", {})

    return {
        "workflow_id": response.workflow_id,
        "final_decision": response.final_decision,
        "risk_level": response.risk_level,
        "risk_score": response.risk_score,
        "suggested_amount": response.suggested_amount,
        "summary": response.summary,
        "decision_reasons": response.report.decision_reasons,
        "policy_references": [
            {"policy_code": reference.policy_code}
            for reference in response.report.policy_references
        ],
        "decision_report_generation": decision_report_generation,
    }


def main() -> None:
    print(json.dumps(run_demo_review(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
