import importlib.util
from pathlib import Path


def _load_stack_module():
    module_path = Path(__file__).resolve().parents[2] / "scripts" / "run_full_demo_stack.py"
    spec = importlib.util.spec_from_file_location("run_full_demo_stack", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_full_demo_stack_check_only_uses_standard_delivery_files():
    module = _load_stack_module()
    project_root = Path(__file__).resolve().parents[2]

    result = module.build_check_report(project_root)

    assert result["files"]["docker-compose.yml"] is True
    assert result["files"]["agent-service/Dockerfile"] is True
    assert result["files"]["backend-service/Dockerfile"] is True
    assert result["files"][".github/workflows/ci.yml"] is True
    assert result["compose_services"]["mysql"] is True
    assert result["compose_services"]["redis"] is True
    assert result["compose_services"]["agent-service"] is True
    assert result["compose_services"]["backend-service"] is True
    assert "docker compose up --build" in "\n".join(result["commands"])
