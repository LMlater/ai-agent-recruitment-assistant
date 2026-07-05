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

    app_vue = "\n".join(
        (
            _read_repo_text("frontend-service/src/App.vue"),
            _read_repo_text("frontend-service/src/pages/LoginPage.vue"),
            _read_repo_text("frontend-service/src/pages/WorkspacePage.vue"),
            _read_repo_text("frontend-service/src/pages/ApplicationDetail.vue"),
        )
    )
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
    app_vue = _read_repo_text("frontend-service/src/pages/ApplicationDetail.vue")

    for expected in (
        "normalizeLogs",
        "normalizeToolCalls",
        "item.agent_name",
        "item.tool_name",
        "item.duration_ms",
        "item.input_summary",
        "item.output_summary",
        "item.error_message",
        "const agentTimeline = computed(() => normalizeLogs(logs.value))",
        "const toolCalls = computed(() => agentTimeline.value.flatMap((agent) => agent.toolCalls))",
        "当前路径未进入 SeniorReviewAgent",
        'item.name || "Agent"',
        "formatDuration(agent.durationMs)",
        "formatDuration(tool.durationMs)",
    ):
        assert expected in app_vue

    assert "const agentTimeline = computed(() => selectedRow.value?.agentResults || [])" not in app_vue
    assert "tool.toolName || tool.name" not in app_vue
    assert "function flattenToolCalls" not in app_vue


def test_round17_frontend_router_auth_and_detail_page_polish():
    required_files = (
        "frontend-service/package-lock.json",
        "frontend-service/src/router.js",
        "frontend-service/src/pages/LoginPage.vue",
        "frontend-service/src/pages/WorkspacePage.vue",
        "frontend-service/src/pages/ApplicationDetail.vue",
    )
    for relative_path in required_files:
        assert (PROJECT_ROOT / relative_path).exists(), relative_path

    package_json = _read_repo_text("frontend-service/package.json")
    package_lock = _read_repo_text("frontend-service/package-lock.json")
    assert '"vue-router"' in package_json
    assert '"vue-router"' in package_lock

    main_js = _read_repo_text("frontend-service/src/main.js")
    assert "router" in main_js
    assert ".use(router)" in main_js

    router_js = _read_repo_text("frontend-service/src/router.js")
    for expected in (
        'path: "/login"',
        'path: "/workspace"',
        'path: "/applications/:applicationId"',
        'redirect: "/workspace"',
        "beforeEach",
        "hasToken()",
        'next("/login")',
    ):
        assert expected in router_js

    api_js = _read_repo_text("frontend-service/src/api.js")
    for expected in (
        "clearToken",
        "hasToken",
        "requireToken",
        "smartcredit.frontend.token",
        "请先登录 demo admin",
    ):
        assert expected in api_js
    assert "requireToken()" in api_js

    app_vue = _read_repo_text("frontend-service/src/App.vue")
    for expected in (
        "<router-view",
        "当前用户：admin",
        "退出登录",
        "未登录",
        "去登录",
        "clearLastBatchRows",
        'router.push("/login")',
    ):
        assert expected in app_vue

    workspace_vue = _read_repo_text("frontend-service/src/pages/WorkspacePage.vue")
    for expected in (
        "smartcredit.frontend.lastBatchRows",
        "saveLastBatchRows",
        "loadLastBatchRows",
        "document.getElementById",
        "scrollIntoView({ behavior: \"smooth\" })",
        "router.push(`/applications/${row.applicationId}`)",
        "重新检测本条",
        "查看详情",
        "runBatchAiReview",
        "for (const row of batchRows.value)",
    ):
        assert expected in workspace_vue

    assert "activeSection = item.id" not in workspace_vue
    assert "Promise.all" not in workspace_vue

    detail_vue = _read_repo_text("frontend-service/src/pages/ApplicationDetail.vue")
    for expected in (
        "getApplication(applicationId)",
        "getAiReports(applicationId)",
        "getAgentLogs",
        "getApprovalHistory(applicationId)",
        "getMaterialUpdates(applicationId)",
        "route.query.tab",
        'name="summary"',
        'name="trace"',
        'name="tools"',
        'name="policy"',
        'name="history"',
        'name="materials"',
        'name="approval"',
        "AI 不自动终审",
    ):
        assert expected in detail_vue

    styles_css = _read_repo_text("frontend-service/src/styles.css")
    for expected in (
        ".sidebar",
        ".capability-tag",
        "cursor: pointer",
        ".detail-shell",
        ".approval-panel",
        "overflow-x: hidden",
    ):
        assert expected in styles_css
