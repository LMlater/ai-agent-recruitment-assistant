import importlib.util
import json
import os
import shutil
from pathlib import Path


def _load_readiness_module():
    module_path = Path(__file__).resolve().parents[2] / "scripts" / "check_demo_readiness.py"
    spec = importlib.util.spec_from_file_location("check_demo_readiness", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_readiness_reports_missing_files():
    module = _load_readiness_module()
    missing_root = Path(__file__).resolve().parents[2] / "__missing_demo_readiness_root__"

    result = module.build_readiness_report(project_root=missing_root, check_services=False)

    assert result["ok"] is False
    assert result["files"]["backend-service"] is False
    assert result["files"]["backend-service/Dockerfile"] is False
    assert result["files"]["agent-service/Dockerfile"] is False
    assert result["files"][".github/workflows/ci.yml"] is False
    assert result["files"]["docs/DEMO_GUIDE.md"] is False
    assert "missing required files" in result["issues"]
    assert "docker compose services missing" in result["issues"]


def test_readiness_reports_required_files_for_current_repo():
    module = _load_readiness_module()
    project_root = Path(__file__).resolve().parents[2]

    result = module.build_readiness_report(project_root=project_root, check_services=False)

    assert result["files"]["backend-service"] is True
    assert result["files"]["agent-service"] is True
    assert result["files"]["scripts/run_e2e_credit_review_demo.py"] is True
    assert result["files"]["scripts/run_full_demo_stack.py"] is True
    assert result["files"]["backend-service/Dockerfile"] is True
    assert result["files"]["agent-service/Dockerfile"] is True
    assert result["files"][".github/workflows/ci.yml"] is True
    assert result["docker_compose"]["exists"] is True
    assert result["docker_compose"]["services"] == {
        "mysql": True,
        "redis": True,
        "agent-service": True,
        "backend-service": True,
    }
    assert "DASHSCOPE_API_KEY" not in json.dumps(result, ensure_ascii=False)


def test_docker_compose_service_check_detects_missing_services():
    module = _load_readiness_module()
    tmp_path = Path(__file__).resolve().parents[2] / ".pytest-local-tmp" / f"compose-check-{os.getpid()}"
    tmp_path.mkdir(parents=True, exist_ok=True)
    compose_file = tmp_path / "docker-compose.yml"
    compose_file.write_text(
        "services:\n  mysql:\n    image: mysql:8\n  redis:\n    image: redis:7\n",
        encoding="utf-8",
    )

    try:
        result = module.check_docker_compose(tmp_path)
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)

    assert result["exists"] is True
    assert result["services"]["mysql"] is True
    assert result["services"]["redis"] is True
    assert result["services"]["agent-service"] is False
    assert result["services"]["backend-service"] is False


def test_unreachable_services_return_false_without_exception():
    module = _load_readiness_module()

    result = module.check_services(
        backend_base_url="http://127.0.0.1:9",
        agent_base_url="http://127.0.0.1:9",
        timeout_seconds=0.2,
    )

    assert result["backend"]["reachable"] is False
    assert result["agent"]["reachable"] is False


def test_readiness_main_does_not_print_api_key_name(capsys):
    module = _load_readiness_module()

    exit_code = module.main(["--skip-services"])

    captured = capsys.readouterr()
    assert exit_code in {0, 1}
    assert "DASHSCOPE_API_KEY" not in captured.out
