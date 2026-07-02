"""Run a backend-driven credit review demo.

This script talks to the Spring Boot backend over HTTP. The backend then calls
agent-service according to its own configuration, so this script never needs or
prints LLM API keys.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from decimal import Decimal
from typing import Any
from urllib import error, request


DEFAULT_BACKEND_BASE_URL = "http://localhost:8080"
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin@123456"


class DemoError(RuntimeError):
    """Raised when the demo cannot continue safely."""


class BackendClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.token: str | None = None

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        *,
        unwrap_result: bool = True,
    ) -> Any:
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        url = f"{self.base_url}{path}"
        http_request = request.Request(url, data=body, headers=headers, method=method)
        try:
            with request.urlopen(http_request, timeout=30) as response:
                response_body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            message = exc.read().decode("utf-8", errors="replace")
            raise DemoError(f"HTTP {exc.code} from backend for {method} {path}: {message}") from exc
        except error.URLError as exc:
            raise DemoError(
                f"Cannot connect to backend at {self.base_url}. Start backend-service first and check BACKEND_BASE_URL."
            ) from exc

        if not response_body:
            return None
        try:
            data = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise DemoError(f"Backend returned non-JSON response for {method} {path}") from exc
        if not unwrap_result:
            return data
        return unwrap_backend_result(data, f"{method} {path}")


def unwrap_backend_result(payload: Any, operation: str) -> Any:
    if not isinstance(payload, dict) or "code" not in payload:
        return payload
    if payload.get("code") != 0:
        message = payload.get("message") or "unknown backend error"
        raise DemoError(f"Backend rejected {operation}: {message}")
    return payload.get("data")


def ensure_admin_user(client: BackendClient, username: str, password: str) -> None:
    try:
        client.request(
            "POST",
            "/api/auth/init-admin",
            {
                "username": username,
                "password": password,
                "displayName": "Demo Admin",
            },
        )
    except DemoError as exc:
        if "Admin initialization is only allowed when no users exist" not in str(exc):
            raise


def login(client: BackendClient, username: str, password: str) -> None:
    data = client.request("POST", "/api/auth/login", {"username": username, "password": password})
    token = _get(data, "token")
    if not token:
        raise DemoError("Backend login did not return a token. Check DEMO_ADMIN_USERNAME and DEMO_ADMIN_PASSWORD.")
    client.token = token


def create_demo_application(client: BackendClient) -> int:
    customer = client.request(
        "POST",
        "/api/customers",
        {
            "name": "E2E Demo Customer",
            "idCardMasked": "4401********2099",
            "phoneMasked": "138****2099",
            "age": 32,
            "monthlyIncome": "12000",
            "workYears": 5,
            "existingDebt": "30000",
            "overdueCount": 0,
            "assetProofCount": 2,
        },
    )
    customer_id = _get(customer, "id")
    if customer_id is None:
        raise DemoError("Customer creation did not return an id.")

    application = client.request(
        "POST",
        "/api/loan-applications",
        {
            "customerId": customer_id,
            "amount": "80000",
            "termMonths": 24,
            "purpose": "E2E interview demo loan",
        },
    )
    application_id = _get(application, "id")
    if application_id is None:
        raise DemoError("Loan application creation did not return an id.")

    client.request("POST", f"/api/loan-applications/{application_id}/submit")
    return int(application_id)


def run_ai_review(client: BackendClient, application_id: int) -> dict[str, Any]:
    response = client.request("POST", f"/api/loan-applications/{application_id}/ai-review")
    if not isinstance(response, dict):
        raise DemoError("AI review did not return an object response.")
    return response


def fetch_reports(client: BackendClient, application_id: int) -> list[dict[str, Any]]:
    reports = client.request("GET", f"/api/loan-applications/{application_id}/ai-reports")
    return reports if isinstance(reports, list) else []


def fetch_logs(client: BackendClient, application_id: int, workflow_id: str | None) -> list[dict[str, Any]]:
    if workflow_id:
        logs = client.request("GET", f"/api/agent-workflows/{workflow_id}/logs")
        if isinstance(logs, list) and logs:
            return logs
    logs = client.request("GET", f"/api/loan-applications/{application_id}/agent-logs")
    return logs if isinstance(logs, list) else []


def apply_manual_decision(client: BackendClient, application_id: int, decision: str | None) -> dict[str, Any] | None:
    if not decision:
        return None
    endpoint_by_decision = {
        "approve": "approve",
        "reject": "reject",
        "need-more-info": "need-more-info",
    }
    endpoint = endpoint_by_decision[decision]
    result = client.request(
        "POST",
        f"/api/approvals/{application_id}/{endpoint}",
        {"comment": f"E2E demo manual decision: {decision}"},
    )
    return result if isinstance(result, dict) else {"result": result}


def build_demo_summary(
    *,
    application_id: int,
    ai_review_response: dict[str, Any],
    reports: list[dict[str, Any]],
    logs: list[dict[str, Any]],
    manual_decision_response: dict[str, Any] | None = None,
) -> dict[str, Any]:
    workflow_id = _get(ai_review_response, "workflow_id", "workflowId")
    report = _get(ai_review_response, "report") or {}
    policy_references = _get(report, "policy_references", "policyReferences") or []

    summary = {
        "application_id": application_id,
        "ai_review_triggered": True,
        "workflow_id": workflow_id,
        "final_decision_from_ai": _get(ai_review_response, "final_decision", "finalDecision"),
        "risk_level": _get(ai_review_response, "risk_level", "riskLevel"),
        "risk_score": _get(ai_review_response, "risk_score", "riskScore"),
        "suggested_amount": _get(ai_review_response, "suggested_amount", "suggestedAmount"),
        "ai_report_id": _first_report_id(reports),
        "agent_log_count": len(logs),
        "decision_agent_llm_provider": _decision_agent_llm_provider(ai_review_response, logs),
        "policy_codes": _policy_codes(policy_references),
        "manual_approval_required": True,
    }
    if manual_decision_response is not None:
        summary["manual_decision_applied"] = True
        summary["manual_decision_status"] = _get(manual_decision_response, "toStatus", "to_status", "decision", "status")
    return summary


def _first_report_id(reports: list[dict[str, Any]]) -> Any:
    if not reports:
        return None
    return _get(reports[0], "id", "reportId")


def _policy_codes(policy_references: Any) -> list[str]:
    if not isinstance(policy_references, list):
        return []
    codes: list[str] = []
    for reference in policy_references:
        code = _get(reference, "policy_code", "policyCode")
        if code and code not in codes:
            codes.append(str(code))
    return codes


def _decision_agent_llm_provider(ai_review_response: dict[str, Any], logs: list[dict[str, Any]]) -> str | None:
    for result in _get(ai_review_response, "agent_results", "agentResults") or []:
        if _get(result, "agent_name", "agentName") != "DecisionAgent":
            continue
        generation = (_get(result, "result") or {}).get("decision_report_generation")
        if isinstance(generation, dict) and generation.get("llm_provider"):
            return str(generation["llm_provider"])

    provider_pattern = re.compile(r"llm_provider=([^,;|\s]+)")
    for log in logs:
        if _get(log, "agent_name", "agentName") != "DecisionAgent":
            continue
        output_summary = _get(log, "output_summary", "outputSummary") or ""
        match = provider_pattern.search(str(output_summary))
        if match:
            return match.group(1)
    return None


def _get(value: Any, *keys: str) -> Any:
    if not isinstance(value, dict):
        return None
    for key in keys:
        if key in value:
            return value[key]
    return None


class DemoJsonEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SmartCredit Java + Python E2E credit review demo.")
    parser.add_argument(
        "--backend-base-url",
        default=os.getenv("BACKEND_BASE_URL", DEFAULT_BACKEND_BASE_URL),
        help="Spring Boot backend base URL. Defaults to BACKEND_BASE_URL or http://localhost:8080.",
    )
    parser.add_argument(
        "--application-id",
        type=int,
        help="Use an existing SUBMITTED or AI_REVIEWED loan application. If omitted, a mock application is created.",
    )
    parser.add_argument(
        "--manual-decision",
        choices=["approve", "reject", "need-more-info"],
        help="Optionally finalize the demo application through the human approval API.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client = BackendClient(args.backend_base_url)
    username = os.getenv("DEMO_ADMIN_USERNAME", DEFAULT_ADMIN_USERNAME)
    password = os.getenv("DEMO_ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)

    try:
        ensure_admin_user(client, username, password)
        login(client, username, password)
        application_id = args.application_id or create_demo_application(client)
        ai_review = run_ai_review(client, application_id)
        workflow_id = _get(ai_review, "workflow_id", "workflowId")
        reports = fetch_reports(client, application_id)
        logs = fetch_logs(client, application_id, workflow_id)
        manual_decision = apply_manual_decision(client, application_id, args.manual_decision)
        summary = build_demo_summary(
            application_id=application_id,
            ai_review_response=ai_review,
            reports=reports,
            logs=logs,
            manual_decision_response=manual_decision,
        )
    except DemoError as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": str(exc),
                    "hint": "Start backend-service and agent-service first; use --application-id with a SUBMITTED or AI_REVIEWED application if needed.",
                },
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    print(json.dumps(summary, ensure_ascii=False, indent=2, cls=DemoJsonEncoder))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
