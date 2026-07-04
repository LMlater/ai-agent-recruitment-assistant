from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read_repo_text(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_ci_workflow_supports_manual_delivery_package_checks():
    workflow = _read_repo_text(".github/workflows/ci.yml")

    assert "workflow_dispatch:" in workflow
    assert "delivery-package:" in workflow
    assert "name: Delivery package checks" in workflow
    assert "needs: [agent-service, backend-service]" in workflow
    assert "docker compose config" in workflow
    assert "python scripts/check_demo_readiness.py --skip-services" in workflow
    assert "  readiness:" not in workflow
    assert "LLM_PROVIDER: mock" in workflow
    assert 'LLM_ENABLE_REAL_API: "false"' in workflow
    assert 'REAL_API_ENABLED: "false"' in workflow


def test_final_acceptance_checklist_covers_release_gates():
    checklist = _read_repo_text("docs/FINAL_ACCEPTANCE_CHECKLIST.md")

    for heading in (
        "功能验收",
        "工程验收",
        "安全边界验收",
        "面试验收",
        "当前已知限制",
    ):
        assert heading in checklist
    for item in (
        "Tool calls",
        "SeniorReviewAgent 高风险分支",
        "Docker Compose 四服务",
        "GitHub Actions 可触发",
        ".env 未被 git 跟踪",
        "AI 不自动最终审批",
        "Windows 普通 `mvn test`",
        "Docker CLI",
        "RAG 使用模拟制度库",
        "ML 是 baseline",
    ):
        assert item in checklist


def test_release_docs_point_to_acceptance_and_freeze_state():
    readme = _read_repo_text("README.md")
    delivery = _read_repo_text("docs/FINAL_INTERVIEW_DELIVERY.md")
    recovery = _read_repo_text("docs/CONVERSATION_RECOVERY.md")
    iteration_log = _read_repo_text("docs/ITERATION_LOG.md")
    project_context = _read_repo_text("PROJECT_CONTEXT.md")
    validation_log = _read_repo_text("docs/VALIDATION_LOG.md")
    readiness_script = _read_repo_text("scripts/check_demo_readiness.py")

    assert "发布前验收" in readme
    assert "docs/FINAL_ACCEPTANCE_CHECKLIST.md" in readme
    assert "GitHub Actions" in readme
    assert "FINAL_ACCEPTANCE_CHECKLIST.md" in delivery
    assert "workflow_dispatch" in delivery
    assert "不建议现场临时打开真实 LLM" in delivery
    assert "第 13 轮" in recovery
    assert "后续只建议" in recovery
    assert "第 13 轮：发布前验收、CI 手动触发与最终验收清单" in iteration_log
    assert "冻结交付状态" in project_context
    assert "第 13 轮：发布前验收与 CI 可触发性" in validation_log
    assert "docs/FINAL_ACCEPTANCE_CHECKLIST.md" in readiness_script


def test_troubleshooting_covers_actions_and_compose_config_failures():
    troubleshooting = _read_repo_text("docs/TROUBLESHOOTING.md")

    for topic in (
        "GitHub Actions 没有 workflow run",
        "workflow_dispatch",
        "手动 Run workflow",
        "push 到 main",
        "Docker Compose config 失败",
        "docker compose version",
        "源码模式",
    ):
        assert topic in troubleshooting
