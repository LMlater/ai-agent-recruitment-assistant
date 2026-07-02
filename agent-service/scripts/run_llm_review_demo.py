from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DEFAULT_TIMEOUT_SECONDS = 90
DEFAULT_MAX_TOKENS = 600
DEFAULT_TEMPERATURE = "0.2"


def _load_local_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def configure_demo_environment(mode: str, compact: bool = False) -> list[str]:
    warnings: list[str] = []
    if mode == "mock":
        os.environ["LLM_PROVIDER"] = "mock"
        os.environ["LLM_ENABLE_REAL_API"] = "false"
    elif mode == "real":
        os.environ["LLM_PROVIDER"] = "dashscope"
        os.environ["LLM_ENABLE_REAL_API"] = "true"
        _load_local_env()
        _set_demo_default("LLM_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS), {"30"})
        _set_demo_default("LLM_MAX_TOKENS", str(DEFAULT_MAX_TOKENS), {"1200"})
        os.environ.setdefault("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)
        missing = [
            name
            for name in ("DASHSCOPE_API_KEY", "DASHSCOPE_BASE_URL", "DASHSCOPE_MODEL")
            if not os.getenv(name)
        ]
        if missing:
            warnings.append(
                "Real LLM demo requested but missing local configuration: "
                + ", ".join(missing)
                + ". The workflow will keep fallback protection enabled."
            )
    elif mode != "env":
        raise ValueError(f"Unsupported demo mode: {mode}")

    if compact:
        _set_demo_default("LLM_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS), {"30"})
        _set_demo_default("LLM_MAX_TOKENS", str(DEFAULT_MAX_TOKENS), {"1200"})
        os.environ.setdefault("LLM_TEMPERATURE", DEFAULT_TEMPERATURE)
    return warnings


def _set_demo_default(name: str, value: str, replace_values: set[str]) -> None:
    current = os.getenv(name)
    if not current or current in replace_values:
        os.environ[name] = value


def build_demo_request(compact: bool = False):
    from app.schemas.review import ReviewRequest

    if compact:
        return ReviewRequest(
            application_id=9002,
            customer={
                "id": 9002,
                "age": 32,
                "monthly_income": 10000,
                "work_years": 5,
                "existing_debt": 42000,
                "overdue_count": 0,
                "asset_proof_count": 2,
            },
            loan_application={
                "amount": 90000,
                "term_months": 18,
                "purpose": "working capital",
            },
        )

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


def run_demo_review(mode: str = "env", compact: bool = False) -> dict[str, Any]:
    warnings = configure_demo_environment(mode, compact)

    from app.workflow.review_workflow import ReviewWorkflow

    response = ReviewWorkflow().run(build_demo_request(compact=compact))
    decision_agent_result = next(
        (item for item in response.agent_results if item.agent_name == "DecisionAgent"),
        None,
    )
    decision_report_generation = {}
    if decision_agent_result:
        decision_report_generation = decision_agent_result.result.get("decision_report_generation", {})

    return {
        "demo_mode": mode,
        "compact": compact,
        "llm_timeout_seconds": _int_env("LLM_TIMEOUT_SECONDS", 30),
        "llm_max_tokens": _int_env("LLM_MAX_TOKENS", 1200),
        "configuration_warnings": warnings,
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


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if not raw:
        return default
    return int(raw)


def _parse_args(argv: list[str] | None = None):
    import argparse

    parser = argparse.ArgumentParser(description="Run a SmartCredit LLM review demo.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--mock", action="store_true", help="Force MockLLMClient and avoid real API calls.")
    mode_group.add_argument("--real", action="store_true", help="Use DashScope/Bailian when local config is present.")
    parser.add_argument("--compact", action="store_true", help="Use shorter demo input and shorter generation defaults.")
    return parser.parse_args(argv)


def _mode_from_args(args) -> str:
    if args.mock:
        return "mock"
    if args.real:
        return "real"
    return "env"


def main() -> None:
    args = _parse_args()
    result = run_demo_review(mode=_mode_from_args(args), compact=args.compact)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
