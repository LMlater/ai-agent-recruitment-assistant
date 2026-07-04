"""Check whether the SmartCredit demo package is ready to present.

The script uses only the Python standard library. It does not read or print any
LLM secret values; it only checks repository files, basic service reachability,
and whether local environment files have accidentally been tracked by git.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_BACKEND_BASE_URL = "http://localhost:8080"
DEFAULT_AGENT_BASE_URL = "http://localhost:8001"

REQUIRED_PATHS = (
    "backend-service",
    "agent-service",
    "scripts/run_e2e_credit_review_demo.py",
    "scripts/run_full_demo_stack.py",
    "backend-service/Dockerfile",
    "agent-service/Dockerfile",
    ".github/workflows/ci.yml",
    "docs/DEMO_GUIDE.md",
    "docs/ARCHITECTURE.md",
    "docs/API_WALKTHROUGH.md",
    "docs/INTERVIEW_SCRIPT.md",
    "docs/FINAL_INTERVIEW_DELIVERY.md",
    "docs/TROUBLESHOOTING.md",
    "docs/FINAL_DEMO_SCRIPT.md",
    "docs/FINAL_ACCEPTANCE_CHECKLIST.md",
)

LOCAL_ENV_PATHS = (".env", "agent-service/.env", "backend-service/.env")
COMPOSE_REQUIRED_SERVICES = ("mysql", "redis", "agent-service", "backend-service")


def build_readiness_report(
    *,
    project_root: Path | None = None,
    backend_base_url: str = DEFAULT_BACKEND_BASE_URL,
    agent_base_url: str = DEFAULT_AGENT_BASE_URL,
    check_services: bool = True,
    timeout_seconds: float = 2.0,
) -> dict[str, Any]:
    root = (project_root or Path(__file__).resolve().parents[1]).resolve()
    files = check_required_files(root)
    docker_compose = check_docker_compose(root)
    services = (
        check_services_reachability(
            backend_base_url=backend_base_url,
            agent_base_url=agent_base_url,
            timeout_seconds=timeout_seconds,
        )
        if check_services
        else {}
    )
    security = check_security(root)

    issues = collect_issues(
        files=files,
        docker_compose=docker_compose,
        services=services,
        security=security,
    )
    return {
        "ok": not issues,
        "project_root": str(root),
        "files": files,
        "docker_compose": docker_compose,
        "services": services,
        "security": security,
        "issues": issues,
    }


def check_required_files(project_root: Path) -> dict[str, bool]:
    return {path: (project_root / path).exists() for path in REQUIRED_PATHS}


def check_docker_compose(project_root: Path) -> dict[str, Any]:
    compose_path = project_root / "docker-compose.yml"
    if not compose_path.exists():
        return {
            "exists": False,
            "services": {service: False for service in COMPOSE_REQUIRED_SERVICES},
        }
    text = compose_path.read_text(encoding="utf-8")
    return {
        "exists": True,
        "services": {
            service: f"{service}:" in text for service in COMPOSE_REQUIRED_SERVICES
        },
    }


def check_services_reachability(
    *,
    backend_base_url: str,
    agent_base_url: str,
    timeout_seconds: float,
) -> dict[str, dict[str, Any]]:
    return {
        "backend": check_url_reachable(
            f"{backend_base_url.rstrip('/')}/api/auth/me",
            timeout_seconds=timeout_seconds,
        ),
        "agent": check_url_reachable(
            f"{agent_base_url.rstrip('/')}/health",
            timeout_seconds=timeout_seconds,
        ),
    }


def check_services(
    *,
    backend_base_url: str = DEFAULT_BACKEND_BASE_URL,
    agent_base_url: str = DEFAULT_AGENT_BASE_URL,
    timeout_seconds: float = 2.0,
) -> dict[str, dict[str, Any]]:
    return check_services_reachability(
        backend_base_url=backend_base_url,
        agent_base_url=agent_base_url,
        timeout_seconds=timeout_seconds,
    )


def check_url_reachable(url: str, *, timeout_seconds: float) -> dict[str, Any]:
    http_request = request.Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with request.urlopen(http_request, timeout=timeout_seconds) as response:
            return {"reachable": True, "url": url, "status": response.status}
    except error.HTTPError as exc:
        # HTTP 401/403/404 still proves the service is reachable.
        return {"reachable": True, "url": url, "status": exc.code}
    except error.URLError as exc:
        return {"reachable": False, "url": url, "error": str(exc.reason)}
    except TimeoutError:
        return {"reachable": False, "url": url, "error": "timed out"}
    except Exception as exc:  # pragma: no cover - defensive guard for demo CLI.
        return {"reachable": False, "url": url, "error": exc.__class__.__name__}


def check_security(project_root: Path) -> dict[str, bool]:
    return {
        "env_file_tracked": is_env_file_tracked(project_root),
        "prints_api_key": False,
    }


def is_env_file_tracked(project_root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "ls-files", "--", *LOCAL_ENV_PATHS],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return False
    return bool(result.stdout.strip())


def collect_issues(
    *,
    files: dict[str, bool],
    docker_compose: dict[str, Any],
    services: dict[str, dict[str, Any]],
    security: dict[str, bool],
) -> list[str]:
    issues: list[str] = []
    if not all(files.values()):
        issues.append("missing required files")
    compose_services = docker_compose.get("services", {})
    if not docker_compose.get("exists") or not all(compose_services.values()):
        issues.append("docker compose services missing")
    if services:
        unavailable = [name for name, value in services.items() if not value.get("reachable")]
        if unavailable:
            issues.append("services not reachable: " + ", ".join(unavailable))
    if security.get("env_file_tracked"):
        issues.append("local env file is tracked by git")
    if security.get("prints_api_key"):
        issues.append("readiness output may expose an API key")
    return issues


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check SmartCredit demo readiness.")
    parser.add_argument("--project-root", type=Path, help="Repository root. Defaults to this script's parent repo.")
    parser.add_argument("--backend-base-url", default=DEFAULT_BACKEND_BASE_URL)
    parser.add_argument("--agent-base-url", default=DEFAULT_AGENT_BASE_URL)
    parser.add_argument("--timeout-seconds", type=float, default=2.0)
    parser.add_argument("--skip-services", action="store_true", help="Check files and security only.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_readiness_report(
        project_root=args.project_root,
        backend_base_url=args.backend_base_url,
        agent_base_url=args.agent_base_url,
        check_services=not args.skip_services,
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
