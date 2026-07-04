"""Check and optionally start the full SmartCredit demo stack.

This script intentionally uses only the Python standard library. It does not
read local .env files or require any API key; the default demo stack runs with
the mock LLM provider.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REQUIRED_FILES = (
    "docker-compose.yml",
    "agent-service/Dockerfile",
    "backend-service/Dockerfile",
    ".github/workflows/ci.yml",
    "scripts/check_demo_readiness.py",
    "docs/FINAL_ACCEPTANCE_CHECKLIST.md",
)
REQUIRED_COMPOSE_SERVICES = ("mysql", "redis", "agent-service", "backend-service")
COMMANDS = (
    "docker compose up --build",
    "Agent health: http://localhost:8001/health",
    "Demo page: http://localhost:8080/demo.html",
)
SOURCE_MODE_COMMANDS = (
    "docker compose up -d mysql redis",
    "cd agent-service && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001",
    "cd backend-service && mvn spring-boot:run",
)


def build_check_report(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    compose_text = _read_text(root / "docker-compose.yml")
    return {
        "ok": True,
        "project_root": str(root),
        "docker": {
            "docker_cli": _command_available(["docker", "--version"]),
            "docker_compose": _command_available(["docker", "compose", "version"]),
        },
        "files": {path: (root / path).exists() for path in REQUIRED_FILES},
        "compose_services": {
            service: f"{service}:" in compose_text
            for service in REQUIRED_COMPOSE_SERVICES
        },
        "readiness": _run_readiness(root),
        "commands": list(COMMANDS),
        "source_mode_commands": list(SOURCE_MODE_COMMANDS),
    }


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _command_available(command: list[str]) -> bool:
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def _run_readiness(project_root: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        "scripts/check_demo_readiness.py",
        "--skip-services",
    ]
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "error": exc.__class__.__name__}

    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        report = {"ok": False, "stdout": result.stdout[-1000:]}
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "report": report,
    }


def normalize_report(report: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    hints: list[str] = []
    if not all(report["files"].values()):
        issues.append("missing delivery files")
    if not all(report["compose_services"].values()):
        issues.append("docker compose services missing")
    if not report["readiness"].get("ok"):
        issues.append("readiness check failed")
    static_ok = not issues
    if not report["docker"]["docker_cli"]:
        issues.append("docker cli not available")
        hints.append("Docker is unavailable; use source mode commands instead.")
    if not report["docker"]["docker_compose"]:
        issues.append("docker compose plugin not available")
        hints.append("Install Docker Desktop or continue with source mode for the interview demo.")
    report["static_ok"] = static_ok
    report["issues"] = issues
    report["hints"] = hints
    report["ok"] = not issues
    return report


def print_next_steps() -> None:
    print("\nCommands and URLs:")
    for item in COMMANDS:
        print(f"- {item}")
    print("\nSource mode fallback:")
    for item in SOURCE_MODE_COMMANDS:
        print(f"- {item}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SmartCredit full demo stack.")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check-only", action="store_true", help="Check prerequisites without starting Docker.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    project_root = args.project_root.resolve()
    report = normalize_report(build_check_report(project_root))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print_next_steps()

    if args.check_only:
        return 0 if report["ok"] else 1
    if not report["docker"]["docker_cli"] or not report["docker"]["docker_compose"]:
        return 1

    result = subprocess.run(["docker", "compose", "up", "--build"], cwd=project_root, check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
