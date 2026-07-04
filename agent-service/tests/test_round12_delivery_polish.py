import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read_repo_text(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def _load_stack_module():
    module_path = PROJECT_ROOT / "scripts" / "run_full_demo_stack.py"
    spec = importlib.util.spec_from_file_location("run_full_demo_stack", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_readme_top_polish_contains_ci_badge_and_demo_entrypoints():
    readme = _read_repo_text("README.md")

    assert "[![CI](https://github.com/LMlater/ai-agent-recruitment-assistant/actions/workflows/ci.yml/badge.svg)]" in readme
    assert "Java 后端/金融科技/AI Agent 工程面试" in readme
    assert "Docker 模式" in readme
    assert "源码模式" in readme
    assert "面试 Demo 流程 7 步" in readme
    assert "不能夸大的边界" in readme
    assert "docs/TROUBLESHOOTING.md" in readme
    assert "docs/FINAL_DEMO_SCRIPT.md" in readme


def test_round12_troubleshooting_doc_covers_known_failure_modes():
    troubleshooting = _read_repo_text("docs/TROUBLESHOOTING.md")

    required_topics = (
        "Docker 未安装",
        "端口占用",
        "MySQL 初始化失败",
        "Agent 服务不可达",
        "Backend 启动失败",
        "GitHub Actions",
        "Windows 本地 Maven target AccessDenied",
        "Mock LLM",
        "Demo 页面操作失败",
    )
    for topic in required_topics:
        assert topic in troubleshooting
    assert "mvn -Dmaven.resources.skip=true test" in troubleshooting
    assert "docker compose down -v" in troubleshooting


def test_round12_final_demo_script_covers_interview_flow_and_questions():
    demo_script = _read_repo_text("docs/FINAL_DEMO_SCRIPT.md")

    assert "3 分钟演示脚本" in demo_script
    assert "5 分钟演示脚本" in demo_script
    assert "面试官追问路线" in demo_script
    for topic in (
        "为什么拆 Java + Python",
        "Tool calling 怎么体现",
        "为什么要 RAG",
        "为什么要 ML baseline",
        "为什么不自动审批",
        "Docker/CI 做了什么",
        "离真实银行生产还差什么",
    ):
        assert topic in demo_script


def test_full_demo_stack_reports_source_mode_fallback_when_docker_missing():
    module = _load_stack_module()

    report = module.normalize_report(
        {
            "ok": True,
            "project_root": str(PROJECT_ROOT),
            "docker": {"docker_cli": False, "docker_compose": False},
            "files": {path: True for path in module.REQUIRED_FILES},
            "compose_services": {service: True for service in module.REQUIRED_COMPOSE_SERVICES},
            "readiness": {"ok": True},
            "commands": list(module.COMMANDS),
        }
    )

    assert report["static_ok"] is True
    assert report["ok"] is False
    assert any("source mode" in hint for hint in report["hints"])
    assert any("docker compose up --build" in command for command in report["commands"])
