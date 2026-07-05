from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read_repo_text(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_round16_demo_page_list_ai_review_has_explicit_loading():
    demo_html = _read_repo_text("backend-service/src/main/resources/static/demo.html")

    assert "isAiReviewAction" in demo_html
    assert "runAiReviewForApplication" in demo_html
    assert "{ aiReview: true }" in demo_html
    assert "AI Review 正在执行：规则评分、ML baseline、Policy RAG、合规检查和真实 LLM 报告生成中" in demo_html
    assert "await fetchPendingApplications()" in demo_html


def test_round16_frontend_workspace_static_assets_exist_and_cover_flow():
    required_files = (
        "frontend-service/package.json",
        "frontend-service/index.html",
        "frontend-service/vite.config.js",
        "frontend-service/src/main.js",
        "frontend-service/src/api.js",
        "frontend-service/src/App.vue",
        "frontend-service/src/styles.css",
    )
    for relative_path in required_files:
        assert (PROJECT_ROOT / relative_path).exists(), relative_path

    package_json = _read_repo_text("frontend-service/package.json")
    assert '"vue"' in package_json
    assert '"vite"' in package_json
    assert '"element-plus"' in package_json
    assert '"build": "vite build"' in package_json

    vite_config = _read_repo_text("frontend-service/vite.config.js")
    assert "http://localhost:8080" in vite_config
    assert "http://localhost:8001" in vite_config

    api_js = _read_repo_text("frontend-service/src/api.js")
    for api_name in (
        "initAdmin",
        "login",
        "downloadCsvTemplate",
        "uploadCsv",
        "aiReview",
        "listApplications",
        "getAiReports",
        "getAgentLogs",
        "manualApprove",
        "manualReject",
        "manualNeedMoreInfo",
        "updateMaterials",
        "resubmit",
        "getApprovalHistory",
        "getMaterialUpdates",
    ):
        assert f"export async function {api_name}" in api_js

    app_vue = _read_repo_text("frontend-service/src/App.vue")
    for expected in (
        "SmartCreditMultiAgent",
        "信贷审批辅助工作台",
        "CSV批量导入",
        "Batch AI Review",
        "Tool Trace",
        "Policy RAG",
        "Human-in-the-loop",
        "Real LLM Report",
        "请选择仓库内置样例文件",
        "docs/sample_import/loan_applications_sample.csv",
        "上传 CSV 导入",
        "批量 AI 检测上传文件",
        "runBatchAiReview",
        "for (const row of batchRows.value)",
        "检测中",
        "检测完成",
        "检测失败",
        "highRiskCount",
        "needMoreInfoCount",
        "approveSuggestionCount",
        "rejectSuggestionCount",
        "Agent Trace",
        "Tool Calls",
        "Policy References",
        "人工通过",
        "人工拒绝",
        "要求补件",
        "提交补件摘要",
        "重新提交",
    ):
        assert expected in app_vue

    assert "Promise.all" not in app_vue
    assert "/batch-import-sample" not in app_vue
    assert "一键导入内置样例" not in app_vue


def test_round16_1_frontend_agent_tool_trace_normalization():
    app_vue = _read_repo_text("frontend-service/src/App.vue")

    for expected in (
        "normalizeAgentResult",
        "normalizeToolCall",
        "normalizeAgentResults",
        "normalizeToolCalls",
        "agent.agent_name",
        "tool.tool_name",
        "agent.duration_ms",
        "tool.duration_ms",
        "agent.input_summary",
        "tool.input_summary",
        "agent.output_summary",
        "tool.output_summary",
        "tool.error_message",
        "const normalizedAgentResults = computed",
        "const agentTimeline = computed(() => normalizedAgentResults.value)",
        'agent.agentName === "SeniorReviewAgent"',
        "当前路径未进入 SeniorReviewAgent，这是正常条件分支。",
        "该 Agent 暂无输出摘要，但状态已记录。",
        "formatDuration(agent.durationMs)",
        "formatDuration(tool.durationMs)",
    ):
        assert expected in app_vue

    assert "const agentTimeline = computed(() => selectedRow.value?.agentResults || [])" not in app_vue
    assert "tool.toolName || tool.name" not in app_vue
    assert "function flattenToolCalls" not in app_vue
