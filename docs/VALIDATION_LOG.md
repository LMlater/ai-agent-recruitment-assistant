# Validation Log

## Round 16.1: Frontend Agent / Tool Trace Normalization

日期：2026-07-05

### targeted Round 16.1 static tests

```powershell
cd agent-service
python -m pytest tests\test_round16_frontend_workspace.py -q
```

结果：通过，`3 passed, 1 warning`。新增覆盖 `normalizeAgentResult`、`normalizeToolCall`、`agent_name`、`tool_name`、`duration_ms`、`input_summary`、`output_summary`、`error_message`，并确认 `hasSeniorReview` 基于 normalized agent name，页面不再依赖 `tool.toolName || tool.name`。

### agent-service

```powershell
cd agent-service
python -m pytest tests -q
```

结果：通过，`75 passed, 1 skipped, 2 warnings`。跳过项仍为真实 LLM smoke 类测试；普通测试保持 Mock LLM，不调用真实 API。警告包括 Starlette/httpx deprecation 和本机 `.pytest_cache` 写入权限警告。

### backend-service

```powershell
cd backend-service
mvn -Dmaven.resources.skip=true test
```

结果：PowerShell 直接执行时将 `-Dmaven.resources.skip=true` 解析异常，Maven 报 `Unknown lifecycle phase ".resources.skip=true"`。随后使用等价的 PowerShell 引号形式：

```powershell
mvn "-Dmaven.resources.skip=true" test
```

结果：进入测试阶段后失败于默认 Maven 本地仓库写入权限，`D:\maven\apache-maven-3.9.9-bin\apache-maven-3.9.9\mvn_repo\...\surefire-junit-platform\3.2.5` 出现 `AccessDeniedException`。本地替代验证使用仓库内 Maven repo：

```powershell
mvn "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" test
```

结果：通过，`Tests run: 34, Failures: 0, Errors: 0, Skipped: 0`。

### frontend-service

```powershell
cd frontend-service
npm run build
```

结果：首次在沙箱内失败于 esbuild 子进程 `spawn EPERM`；提权后通过，`vite v6.4.3` 构建成功，`1590 modules transformed`。保留 Vite/Rollup 的大 chunk 与 `#__PURE__` 注释位置警告。

### 安全记录

- 本轮只修正式前端展示层字段归一化，不改 Java 后端业务逻辑，不改 Python Agent 流程，不改审批状态机。
- 未提交 `.env`、真实 API Key、本地敏感配置、真实身份证、真实手机号、征信报告或银行流水。

## Round 16: Batch File AI Review + Formal Frontend Workspace

日期：2026-07-05

### TDD 红灯记录

```powershell
cd agent-service
python -m pytest tests\test_round16_frontend_workspace.py -q
```

结果：按预期失败，失败点包括 `demo.html` 尚未包含 `isAiReviewAction`，以及 `frontend-service/package.json` 等正式前端文件尚不存在。

### targeted Round 16 static tests

```powershell
cd agent-service
python -m pytest tests\test_round16_frontend_workspace.py -q
```

结果：通过，`2 passed`。覆盖 `demo.html` 列表 AI 预审 loading 修复锚点、`frontend-service` Vue/Vite/Element Plus 文件、API 封装、顺序批量 AI 检测、Agent Trace、Tool Calls、Policy References 和人工审批文案。

```powershell
cd backend-service
mvn "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" "-Dtest=DemoPageStaticTest" test
```

结果：通过，`Tests run: 1, Failures: 0, Errors: 0, Skipped: 0`。

### agent-service

```powershell
cd agent-service
python -m pytest tests -q
```

结果：通过，`74 passed, 1 skipped, 2 warnings`。跳过项仍为真实 LLM smoke 类测试；普通测试保持 Mock LLM，不调用真实 API。警告包括 Starlette/httpx deprecation 和本机 `.pytest_cache` 写入权限警告。

### readiness

```powershell
python scripts\check_demo_readiness.py --skip-services
```

结果：通过，`ok=true`。readiness 现在也检查 `frontend-service/package.json`、`frontend-service/src/App.vue`、`frontend-service/src/api.js` 等正式前端关键文件；`env_file_tracked=false`、`prints_api_key=false`。

### backend-service

```powershell
cd backend-service
mvn test
```

结果：当前 Windows 本机环境失败，原因为 Maven resources 插件复制 `src/main/resources/static/demo.html` 到 `target/classes/static/demo.html` 时出现 `AccessDeniedException`。这是本地 target 资源复制权限问题，未伪造为通过。

本地替代验证：

```powershell
mvn "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" test
```

结果：通过，`Tests run: 34, Failures: 0, Errors: 0, Skipped: 0`。该命令只作为本机权限问题下的 Java 测试逻辑验证，不替代 CI 的普通 `mvn test`。

### frontend-service

```powershell
cd frontend-service
npm run build
```

结果：未运行成功，当前本机没有 `npm` 命令，PowerShell 返回 `The term 'npm' is not recognized`。未伪造前端 build 通过；需要安装 Node/npm 后执行 `npm install` 和 `npm run build`。

### 安全记录

- 本轮没有提交 `.env`、真实 API Key、本地敏感配置、真实身份证、真实手机号、征信报告或银行流水。
- 批量 AI 检测顺序调用已有单笔 AI Review 接口，不新增自动最终审批逻辑。
- 最终 `APPROVED / REJECTED / NEED_MORE_INFO` 仍由人工审批接口确认。

## Round 15.1: Clarify Project CSV Fixture Upload Flow

日期：2026-07-05

### TDD 红灯记录

```powershell
cd backend-service
mvn "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" "-Dtest=DemoPageStaticTest" test
```

结果：按预期失败，页面尚未包含 `上传 CSV 导入`、`项目已内置一份脱敏 CSV 样例文件`、`选择文件` 和 `docs/sample_import/loan_applications_sample.csv` 等 Round 15.1 文案锚点。

### targeted backend static test

```powershell
cd backend-service
mvn "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" "-Dtest=DemoPageStaticTest" test
```

结果：通过，`Tests run: 1, Failures: 0, Errors: 0, Skipped: 0`。静态测试确认页面展示项目内置 CSV fixture 路径、`上传 CSV 导入`、手动选择文件提示，并确认页面不包含自动导入内置样例按钮或绕过上传的样例接口路径。

### agent-service

```powershell
cd agent-service
python -m pytest tests -q
```

结果：通过，`72 passed, 1 skipped, 2 warnings`。跳过项仍为真实 LLM smoke 类测试；普通测试保持 Mock LLM，不调用真实 API。警告包括 Starlette/httpx deprecation 和本机 `.pytest_cache` 写入权限警告。

### readiness

```powershell
python scripts\check_demo_readiness.py --skip-services
```

结果：通过，`ok=true`。静态文件、Docker Compose 四服务、最终交付文档和安全检查均通过，`env_file_tracked=false`、`prints_api_key=false`。

### backend-service

```powershell
cd backend-service
mvn test
```

结果：当前 Windows 本机环境失败，原因为 Maven resources 插件复制 `src/main/resources/static/demo.html` 到 `target/classes/static/demo.html` 时出现 `AccessDeniedException`。这是本地 target 资源复制权限问题，未伪造为通过。

本地替代验证：

```powershell
mvn "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" test
```

结果：通过，`Tests run: 34, Failures: 0, Errors: 0, Skipped: 0`。该命令只作为本机权限问题下的 Java 测试逻辑验证，不替代 CI 的普通 `mvn test`。

### 安全记录

- 本轮没有提交 `.env`、真实 API Key、本地敏感配置、真实身份证、真实手机号、征信报告或银行流水。
- 没有新增绕过文件上传的样例导入接口或按钮。
- CSV fixture 仍为 `docs/sample_import/loan_applications_sample.csv`，用于演示者手动上传测试批量导入。

## 第 15 轮：批量申请导入与中文审批工作台

日期：2026-07-05

### TDD 红灯记录

```powershell
cd backend-service
mvn "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" "-Dtest=LoanApplicationImportServiceTest,DemoPageStaticTest" test
```

结果：按预期编译失败，因为 `LoanApplicationImportService` 尚未实现。这是本轮后端导入服务的红灯测试。

### targeted backend tests

```powershell
cd backend-service
mvn "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" "-Dtest=LoanApplicationImportServiceTest,DemoPageStaticTest" test
```

结果：通过，`Tests run: 4, Failures: 0, Errors: 0, Skipped: 0`。覆盖 CSV 导入成功/失败混合场景、完整身份证/手机号拦截、`.xlsx` 提示、客户字段映射和 demo 静态锚点。

### agent-service

```powershell
cd agent-service
python -m pytest tests -q
```

结果：通过，`72 passed, 1 skipped, 2 warnings`。跳过项仍为真实 LLM smoke 类测试；普通测试保持 Mock LLM，不调用真实 API。警告包括 Starlette/httpx deprecation 和本机 `.pytest_cache` 写入权限警告。

### readiness

```powershell
python scripts\check_demo_readiness.py --skip-services
```

结果：通过，`ok=true`。静态文件、Docker Compose 四服务、最终交付文档和安全检查均通过，`env_file_tracked=false`、`prints_api_key=false`。

### backend-service

```powershell
cd backend-service
mvn test
```

结果：当前 Windows 本机环境失败，原因为 Maven resources 插件复制 `src/main/resources/static/demo.html` 到 `target/classes/static/demo.html` 时出现 `AccessDeniedException`。这是本地 target 资源复制权限问题，未伪造为通过。

本地替代验证：

```powershell
mvn "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" test
```

结果：通过，`Tests run: 34, Failures: 0, Errors: 0, Skipped: 0`。该命令只作为本机权限问题下的 Java 测试逻辑验证，不替代 CI 的普通 `mvn test`。

### 安全记录

- 本轮没有提交 `.env`、真实 API Key、本地敏感配置、真实身份证、真实手机号、征信报告或银行流水。
- 示例 CSV 只包含脱敏/模拟数据。
- AI/ML/RAG/LLM 仍只生成审批辅助建议；最终 `APPROVED` / `REJECTED` / `NEED_MORE_INFO` 仍由人工审批接口完成。

## 第 14 轮：Demo UI Polish 与真实 LLM 等待体验

日期：2026-07-05

### TDD 红灯记录

```powershell
cd agent-service
python -m pytest tests/test_round14_demo_ui_polish.py -q
```

结果：按预期失败，`demo.html` 尚未包含 `Human-in-the-loop`、`Tool Trace`、`Real LLM Report`、`重新开始演示`、真实 LLM 30-90 秒等待提示和终态解释等 Round 14 UI 锚点。

### agent-service

```powershell
cd agent-service
python -m pytest tests -q
```

结果：通过，`72 passed, 1 skipped, 2 warnings in 5.52s`。跳过项仍为真实 LLM smoke 类测试；普通测试保持 Mock LLM，不调用真实 API。警告包括 Starlette/httpx deprecation 和本机 `.pytest_cache` 写入权限警告。

### readiness

```powershell
python scripts\check_demo_readiness.py --skip-services
```

结果：通过，`ok=true`。静态文件、Docker Compose 四服务、最终交付文档和安全检查均通过，`env_file_tracked=false`、`prints_api_key=false`。

### backend-service

```powershell
cd backend-service
mvn test
```

结果：当前 Windows 本机环境失败，原因为 Maven resources 插件复制 `src/main/resources/static/demo.html` 到 `target/classes/static/demo.html` 时出现 `AccessDeniedException`。这是本地 target 资源复制权限问题，未伪造为通过。

本地替代验证：

```powershell
mvn "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" test
```

结果：通过，`Tests run: 31, Failures: 0, Errors: 0, Skipped: 0`。该命令只作为本机权限问题下的 Java 测试逻辑验证，不替代 CI 的普通 `mvn test`。

### 本地真实 LLM 与 Redis

- 本轮未调用真实 LLM API；用户此前确认本地 DashScope/OpenAI-compatible 配置可用，页面已明确提示真实 LLM 报告生成可能需要 30-90 秒。
- Redis 当前本机不可用，但不是 demo 主链路强依赖；排障文档已记录无 Redis 时 backend-service 仍可先启动验证核心链路。

### 安全记录

- 未提交 `.env`、真实 API Key、真实客户数据、真实身份证、手机号、征信报告或银行流水。
- Demo 页面新增高风险样例仍为脱敏 mock fixture。
- AI/ML/RAG/LLM 仍只生成审批辅助建议，最终 `APPROVED` / `REJECTED` 必须走人工按钮。

## 第 13 轮：发布前验收与 CI 可触发性

日期：2026-07-04

### TDD 红灯记录

```powershell
cd agent-service
python -m pytest tests\test_round13_release_acceptance.py -q
```

结果：按预期失败，失败点包括 CI workflow 缺少 `workflow_dispatch` 和 `delivery-package`、`docs/FINAL_ACCEPTANCE_CHECKLIST.md` 不存在、README 缺少发布前验收入口、Troubleshooting 缺少 Actions workflow run 与 Docker Compose config 排障说明。

### agent-service

```powershell
cd agent-service
python -m pytest tests -q
```

结果：通过，`70 passed, 1 skipped, 2 warnings`。跳过项仍为真实 LLM smoke 类测试；普通测试保持 Mock LLM，不调用真实 API。

### backend-service

```powershell
cd backend-service
mvn test
```

结果：当前 Windows 本机环境失败，原因为 Maven resources 插件复制 `src/main/resources/db/schema.sql` 到 `target/classes/db/schema.sql` 时出现 `AccessDeniedException`。这是本地已知文件权限问题；CI 的 Linux runner 仍配置为执行 plain `mvn test`。

本地替代验证：

```powershell
mvn -q "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" test
```

结果：通过，退出码 `0`。

### readiness

```powershell
python scripts\check_demo_readiness.py --skip-services
```

结果：通过，`ok=true`。检查项包含 `docs/FINAL_ACCEPTANCE_CHECKLIST.md`，Compose 四服务结构仍为 `mysql`、`redis`、`agent-service`、`backend-service`，`.env` 未被 git 跟踪。

### full demo stack check

```powershell
python scripts\run_full_demo_stack.py --check-only
```

结果：脚本正常输出报告；当前机器没有 Docker CLI，因此返回 `ok=false`，issues 为 `docker cli not available`、`docker compose plugin not available`。静态交付检查为 `static_ok=true`，readiness 子检查通过，并输出 source mode fallback 命令。

### Docker

```powershell
docker compose config
```

结果：未执行成功，当前环境提示 `docker` 命令不存在。因此本轮无法在本机验证 `docker compose config` 或 `docker compose up --build`；CI 中已新增 `docker compose config` 静态校验，实际 run 结果需要到 GitHub Actions 页面确认。

### GitHub Actions

- 本轮新增 `workflow_dispatch`，便于在 GitHub Actions 页面手动触发 CI。
- CI 实际 run 是否成功仍需要到 GitHub Actions 页面确认。

### 安全记录

- 本轮不新增业务功能，不修改审批状态机、Agent 主流程或数据库业务表。
- 未提交 `.env`、真实 API Key、真实客户数据、真实征信报告或真实银行数据。
- 默认仍为 Mock LLM；最终 `APPROVED` / `REJECTED` 仍必须由人工审批接口确认。

## 第 12 轮最终交付 Polish 验证

日期：2026-07-04

### TDD 红灯记录

```powershell
cd agent-service
python -m pytest tests\test_round12_delivery_polish.py -q
```

结果：按预期失败，失败点包括 README 缺少 CI badge 和最终交付入口、`docs/TROUBLESHOOTING.md` 不存在、`docs/FINAL_DEMO_SCRIPT.md` 不存在、`run_full_demo_stack.py` 尚未输出 `static_ok` 和 source mode fallback hints。

### agent-service

```powershell
cd agent-service
python -m pytest tests -q
```

结果：通过，`66 passed, 1 skipped, 2 warnings`。跳过项仍为真实 LLM smoke 类测试；普通测试保持 Mock LLM，不调用真实 API。

### readiness

```powershell
python scripts\check_demo_readiness.py --skip-services
```

结果：通过，`ok=true`。本轮新增检查项包括 `docs/TROUBLESHOOTING.md` 和 `docs/FINAL_DEMO_SCRIPT.md`，Compose 四服务结构仍为 `mysql`、`redis`、`agent-service`、`backend-service`。

### full demo stack check

```powershell
python scripts\run_full_demo_stack.py --check-only
```

结果：脚本正常输出报告；当前机器没有 Docker CLI，因此返回 `ok=false`，issues 为 `docker cli not available`、`docker compose plugin not available`。静态交付检查为 `static_ok=true`，并输出 source mode fallback 命令。

### Docker

```powershell
docker compose config
```

结果：未执行成功，当前环境提示 `docker` 命令不存在。因此本轮无法在本机验证 `docker compose config` 或 `docker compose up --build`。

### backend-service

```powershell
cd backend-service
mvn test
```

结果：当前 Windows 本机环境失败，原因为 Maven resources 插件复制 `schema.sql` 到 `target/classes` 时出现 `AccessDeniedException`。这是本地已知文件权限问题；CI 的 Linux runner 仍配置为执行 plain `mvn test`。

本地替代验证：

```powershell
mvn -q "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" test
```

结果：通过，退出码 `0`。

### 安全记录

- 未提交 `.env`、真实 API Key、真实客户数据、真实征信报告或真实银行数据。
- 本轮只做最终交付 polish、故障排查手册、最终演示脚本和文档收口。
- 未新增业务功能，未修改第 8/9/10/11 轮核心逻辑。
- 默认仍为 Mock LLM；最终 `APPROVED` / `REJECTED` 仍必须由人工审批接口确认。

## 可视化 Demo 页面验证

日期：2026-07-03

### 面试展示版优化

- 页面已从调试式按钮面板优化为两个 Tab：`客户申请端` 和 `银行审批工作台`。
- 客户申请端新增“一键准备演示数据”，自动执行 init admin、login、create customer、create loan application 和 submit application；admin 已存在时不会中断。
- 银行审批工作台用卡片展示申请详情、AI Review Summary、LLM 信息、制度引用、Agent 日志时间线、人工审批和审批历史。
- Agent Logs 已改为时间线样式，并通过 `translateSummary(text)` 将常见英文摘要翻译为中文。
- Raw JSON Panel 默认折叠，提供“查看最近一次接口响应 JSON”“查看完整 AI Report JSON”“复制 JSON”。
- 页面展示 `LLM Provider`、`LLM Used`、`LLM Error`，默认仍为 `mock`，不会默认调用真实百炼。
- 本轮只优化 `demo.html` 展示层和文档，未修改后端业务逻辑、数据库表结构或 AI review 审批边界。

### 页面入口

```text
http://localhost:8080/demo.html
```

验证方式：在本地两个服务均启动后，打开页面并按页面按钮顺序完整手动点击一遍。

### readiness

```powershell
python scripts\check_demo_readiness.py
```

结果：通过，`ok=true`，`backend.reachable=true`，`agent.reachable=true`，`env_file_tracked=false`，`prints_api_key=false`。

### 页面点击流程

- 页面可打开。
- backend 状态检查成功。
- agent-service 状态检查成功。
- demo admin 初始化步骤可继续执行；admin 已存在时页面不会崩溃。
- demo admin 登录成功。
- demo customer 创建成功。
- loan application 创建成功。
- submit 成功。
- AI Review 成功。
- AI Review Summary 展示成功，`risk_level=LOW`，`risk_score=100`，`ai_report_id=8`。
- Policy References 展示成功，制度编号为 `R-004`、`M-003`、`P-002`、`P-003`、`P-004`。
- Agent Logs 展示成功，共 `5` 个 Agent 且均为 `SUCCESS`：IntakeAgent、RiskAgent、PolicyAgent、ComplianceAgent、DecisionAgent。
- DecisionAgent 的 `outputSummary` 显示 `llm_provider=mock`，`llm_error=null`。
- Approve 人工审批成功，审批历史显示 `AI_REVIEWED -> APPROVED`，comment 为 `visual demo manual decision: approve`。
- Raw JSON Panel 正常显示最近一次接口响应，统一返回格式为 `code/message/data`。
- 前端收尾优化已生效：AI Review 成功后 Loan Application Card 状态显示 `AI_REVIEWED`；人工审批成功后显示最终状态、刷新审批历史、禁用 Approve/Reject/Need More Info，并提示重新演示需准备新的演示申请。

### 边界说明

- 本次页面验证使用 `mock` LLM，没有调用真实百炼。
- AI Review 只给出审批辅助建议，最终 `APPROVED` 由人工审批接口写入。
- Java 后端保存了 AI report，并能查询到 5 条 Agent logs。
- 未记录 MySQL 密码，未记录 API Key。
- 未提交 `.env`、`application-local.yml`、`*.local` 或任何本地配置文件。
- 未改数据库表结构，未让 AI 自动审批最终状态。

### 测试结果

```powershell
cd backend-service
mvn -q "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" test
```

结果：通过，退出码 `0`。

```powershell
cd agent-service
python -m pytest tests -q
```

结果：通过，`57 passed, 1 skipped, 2 warnings in 8.11s`。跳过项为真实 DashScope/Bailian smoke test；普通测试继续使用 Mock，不调用真实百炼。

## 真实双服务 E2E 联调验证

日期：2026-07-03

### readiness

```powershell
python scripts\check_demo_readiness.py
```

结果：通过，`ok=true`。输出摘要：

```json
{
  "backend": {"reachable": true},
  "agent": {"reachable": true},
  "security": {
    "env_file_tracked": false,
    "prints_api_key": false
  }
}
```

本次 readiness 只记录服务可达性和安全检查结果，不记录 MySQL 密码或任何 API Key。

### E2E demo

```powershell
python scripts\run_e2e_credit_review_demo.py
```

结果：通过。输出摘要：

```json
{
  "application_id": 5,
  "ai_review_triggered": true,
  "workflow_id": "36a3af22-51b3-443c-8713-3e6ba9657586",
  "final_decision_from_ai": "APPROVE",
  "risk_level": "LOW",
  "risk_score": 100,
  "suggested_amount": 80000.0,
  "ai_report_id": 3,
  "agent_log_count": 5,
  "decision_agent_llm_provider": "mock",
  "policy_codes": ["R-004", "M-003", "P-002", "P-003", "P-004"],
  "manual_approval_required": true
}
```

说明：Java 后端已保存 AI report，Agent logs 数量为 `5`。`final_decision_from_ai` 是 AI 审批辅助建议，不是最终数据库审批状态。

### 人工审批 demo

```powershell
python scripts\run_e2e_credit_review_demo.py --application-id 5 --manual-decision approve
```

结果：通过。输出摘要：

```json
{
  "application_id": 5,
  "ai_review_triggered": true,
  "workflow_id": "65aa00cd-2326-4e58-ad76-175932341d25",
  "final_decision_from_ai": "APPROVE",
  "risk_level": "LOW",
  "risk_score": 100,
  "suggested_amount": 80000.0,
  "ai_report_id": 4,
  "agent_log_count": 5,
  "decision_agent_llm_provider": "mock",
  "policy_codes": ["R-004", "M-003", "P-002", "P-003", "P-004"],
  "manual_approval_required": true,
  "manual_decision_applied": true,
  "manual_decision_status": "APPROVED"
}
```

说明：最终 `APPROVED` 由人工审批接口完成，AI review 没有自动写入最终审批状态。

### 安全与边界

- 本次使用 `mock` LLM，未调用真实百炼。
- 未记录 MySQL 密码，未记录 API Key。
- 未提交 `.env`、`application-local.yml`、`*.local` 或任何本地配置文件。
- 未改业务代码，未改数据库表结构。

## 本地真实双服务 E2E 联调验证

日期：2026-07-03

### MySQL 与后端启动方式

使用 PowerShell 当前终端环境变量启动 `backend-service`，没有修改 `application.yml`，没有提交任何本地配置文件：

```powershell
$env:MYSQL_URL="jdbc:mysql://localhost:3306/smart_credit_multi_agent?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="[REDACTED]"
$env:AGENT_SERVICE_BASE_URL="http://localhost:8001"
mvn spring-boot:run
```

本地 MySQL 数据库 `smart_credit_multi_agent` 已存在；本次联调前使用项目自带 `backend-service/src/main/resources/db/schema.sql` 和 `data.sql` 初始化，初始化后表数量为 `9`。

### readiness

```powershell
python scripts\check_demo_readiness.py
```

结果：通过，退出码 `0`，`ok=true`。输出摘要：

```json
{
  "backend": {"reachable": true, "status": 400},
  "agent": {"reachable": true, "status": 200},
  "security": {
    "env_file_tracked": false,
    "prints_api_key": false
  },
  "issues": []
}
```

### E2E demo

```powershell
python scripts\run_e2e_credit_review_demo.py
```

结果：通过。输出摘要：

```json
{
  "application_id": 4,
  "workflow_id": "4163fdf5-944f-4444-a4a3-64ff2a673372",
  "final_decision_from_ai": "APPROVE",
  "risk_level": "LOW",
  "risk_score": 100,
  "suggested_amount": 80000.0,
  "ai_report_id": 1,
  "agent_log_count": 5,
  "decision_agent_llm_provider": "mock",
  "policy_codes": ["R-004", "M-003", "P-002", "P-003", "P-004"],
  "manual_approval_required": true
}
```

### 人工审批演示

```powershell
python scripts\run_e2e_credit_review_demo.py --application-id 4 --manual-decision approve
```

结果：通过。输出摘要：

```json
{
  "application_id": 4,
  "workflow_id": "5ff812b6-8ff5-4ed6-b131-236a1f1693e6",
  "final_decision_from_ai": "APPROVE",
  "risk_level": "LOW",
  "risk_score": 100,
  "suggested_amount": 80000.0,
  "ai_report_id": 2,
  "agent_log_count": 5,
  "decision_agent_llm_provider": "mock",
  "policy_codes": ["R-004", "M-003", "P-002", "P-003", "P-004"],
  "manual_approval_required": true,
  "manual_decision_applied": true,
  "manual_decision_status": "APPROVED"
}
```

### 测试结果

```powershell
cd agent-service
$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests -q -p no:cacheprovider
```

结果：通过。输出摘要：`57 passed, 1 skipped, 1 warning in 15.07s`。

```powershell
cd backend-service
mvn -q "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" test
```

结果：通过，退出码 `0`。

### 安全记录

- 本轮使用环境变量修复本地 MySQL 连接，没有修改 `application.yml` 默认密码。
- 真实 MySQL 密码未写入 README、docs、脚本、测试或 git 跟踪文件。
- 未提交 `.env`、`*.local`、`application-local.yml` 或 API Key。
- 本轮未调用真实百炼，`decision_agent_llm_provider=mock`。
- 未修改数据库表结构，未让 AI 自动审批最终状态；最终状态通过人工审批接口写入。

## 第 6 轮演示包装与面试交付版验证

日期：2026-07-02

### readiness script

```powershell
python scripts\check_demo_readiness.py
```

结果：脚本正常输出 JSON，没有 Python stack trace。当前未启动 backend-service 和 agent-service，因此返回退出码 `1`，`ok=false`，文件检查全部为 `true`，安全检查显示 `env_file_tracked=false`、`prints_api_key=false`，服务检查显示：

```json
{
  "backend": {"reachable": false},
  "agent": {"reachable": false}
}
```

这是真实环境状态记录，未伪造双服务联调成功。

```powershell
python scripts\check_demo_readiness.py --skip-services
```

结果：通过，退出码 `0`。输出摘要：`ok=true`，关键文件齐全，`.env` 未被 git 跟踪，readiness 输出不包含真实 API Key。

### agent-service

```powershell
cd agent-service
$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests -q -p no:cacheprovider
```

结果：通过。输出摘要：`57 passed, 1 skipped, 1 warning in 3.67s`。跳过项为真实 DashScope/Bailian smoke test，普通测试仍强制 Mock，不调用真实百炼。

### backend-service

```powershell
cd backend-service
mvn -q "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" test
```

结果：通过，退出码 `0`。继续使用仓库内 `.m2` 作为 Maven 本地仓库路径，以避免当前沙箱默认外部 Maven 仓库路径访问拒绝问题。

### 第 6 轮安全检查

- `.env` 未提交，`.gitignore` 仍包含 `.env`。
- 文档只包含本地 demo admin 示例和 API Key 占位说明，不包含真实 API Key。
- `scripts/check_demo_readiness.py` 不读取、不打印真实 LLM 密钥。
- 本轮未调用真实百炼，未修改 Java 数据库表结构，未让 AI 自动审批最终状态。

### 下一步建议

- 面试前先运行 `python scripts\check_demo_readiness.py --skip-services` 检查文件和安全状态。
- 启动 agent-service 和 backend-service 后，再运行 `python scripts\check_demo_readiness.py` 验证服务可达。
- 真正演示 E2E 前按 `docs/DEMO_GUIDE.md` 的顺序执行，不要把服务未启动状态说成联调成功。

## 第 5 轮端到端演示闭环验证

日期：2026-07-02

### agent-service

```powershell
cd agent-service
$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests -q -p no:cacheprovider
```

结果：通过。输出摘要：`53 passed, 1 skipped, 1 warning in 3.50s`。跳过项为真实 DashScope/Bailian smoke test，普通测试未调用真实百炼。

```powershell
python scripts\run_llm_review_demo.py --mock
```

结果：通过。输出包含 `workflow_id`、`final_decision=NEED_MORE_INFO`、`risk_level=MEDIUM`、`risk_score=78`、policy codes，以及 `decision_report_generation.llm_provider=mock`。未输出 API Key。

```powershell
$env:LLM_PROVIDER='mock'; $env:LLM_ENABLE_REAL_API='false'; python scripts\run_llm_review_demo.py --compact
```

结果：通过。输出包含 `workflow_id`、`final_decision=APPROVE`、`risk_level=LOW`、`risk_score=97`、policy codes，以及 `decision_report_generation.llm_provider=mock`。为避免本地环境变量触发真实 provider，本次自动验证显式覆盖为 Mock。

### backend-service

```powershell
cd backend-service
mvn -q "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" test
```

结果：通过，退出码 `0`。使用仓库内 `.m2` 作为 Maven 本地仓库路径；默认外部 Maven 仓库路径在当前沙箱中曾出现访问拒绝。

覆盖点：

- Java 可以反序列化 Python `/api/v1/reviews` 返回中的结构化 `policy_references`。
- Java 可以保留 `AgentResult.result.decision_report_generation` 嵌套对象。
- `AgentReviewService` 保存 `report_json` 时保留结构化制度引用。
- `AgentReviewService` 将 DecisionAgent 的 `llm_used`、`llm_provider`、`llm_error` 摘要保存到现有 `agent_execution_log.output_summary`。
- AI review 后状态仍写入 `AI_REVIEWED`，不直接写入 `APPROVED` 或 `REJECTED`。
- `DRAFT`、`APPROVED`、`REJECTED`、`NEED_MORE_INFO` 等状态会拒绝 AI review。

### project-level E2E demo script

```powershell
python scripts\run_e2e_credit_review_demo.py --application-id 1
```

结果：当前未启动 backend-service，因此脚本按预期返回清晰错误并退出 `1`：

```json
{
  "ok": false,
  "error": "Cannot connect to backend at http://localhost:8080. Start backend-service first and check BACKEND_BASE_URL.",
  "hint": "Start backend-service and agent-service first; use --application-id with a SUBMITTED or AI_REVIEWED application if needed."
}
```

未伪造端到端服务联调成功。实际联调前需要先启动：

```powershell
cd agent-service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

```powershell
cd backend-service
mvn spring-boot:run
```

然后从仓库根目录运行：

```powershell
python scripts\run_e2e_credit_review_demo.py
python scripts\run_e2e_credit_review_demo.py --application-id 1
python scripts\run_e2e_credit_review_demo.py --application-id 1 --manual-decision approve
```

### safety check

- `.env` 未提交，`.gitignore` 仍包含 `.env`。
- 文档只包含占位符和命令示例，不包含真实 API Key。
- demo 输出不打印 `DASHSCOPE_API_KEY`。
- 普通 Python 测试通过 `tests/conftest.py` 强制 Mock LLM。
- 本轮未修改 Java 数据库表结构。
# 第 11 轮 CI + Docker Compose 工程包装验证

日期：2026-07-04

### TDD 红灯记录

```powershell
cd agent-service
python -m pytest tests\test_check_demo_readiness.py tests\test_run_full_demo_stack.py -q
```

结果：按预期失败。readiness 尚未包含 Dockerfile、CI workflow、Compose 四服务检查，`scripts/run_full_demo_stack.py` 尚不存在。

```powershell
cd backend-service
mvn -q -Dtest=DeliveryPackagingStaticTest test
```

结果：当前 Windows 环境在资源复制阶段出现 `AccessDeniedException`，未进入新增静态测试断言；随后使用仓库内 Maven repo 和资源跳过参数验证新增静态测试。

### agent-service

```powershell
cd agent-service
python -m pytest tests -q
```

结果：通过，`62 passed, 1 skipped, 2 warnings`。跳过项仍为真实 LLM smoke 类测试；普通测试保持 Mock LLM，不调用真实 API。

### backend-service

```powershell
cd backend-service
mvn -q "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" test
```

结果：当前 Windows 本机环境失败，原因为 Maven resources 插件复制 `schema.sql` 到 `target/classes` 时出现 `AccessDeniedException`。这是本地文件权限问题；CI 的 Linux 环境仍配置为执行 plain `mvn test`。

本地替代验证：

```powershell
mvn -q "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" "-Dmaven.resources.skip=true" test
```

结果：通过，退出码 `0`。

### readiness

```powershell
python scripts\check_demo_readiness.py --skip-services
```

结果：通过，`ok=true`。检查项包含 `backend-service/Dockerfile`、`agent-service/Dockerfile`、`.github/workflows/ci.yml`、`scripts/run_full_demo_stack.py`、`docs/FINAL_INTERVIEW_DELIVERY.md` 和 Compose 四服务 `mysql`、`redis`、`agent-service`、`backend-service`。

### full demo stack check

```powershell
python scripts\run_full_demo_stack.py --check-only
```

结果：脚本正常输出检查报告和启动 URL，但当前机器未安装/不可访问 Docker CLI，返回 `ok=false`，issues 为 `docker cli not available`、`docker compose plugin not available`。文件、Compose 服务结构和 readiness 子检查均通过。

```powershell
docker compose config
```

结果：未执行成功，当前环境提示 `docker` 命令不存在。因此本轮无法在本机验证 `docker compose config`、`docker compose build` 或 `docker compose up --build`。

### 安全记录

- 未提交 `.env`、真实 API Key、真实客户数据或真实生产密码。
- Docker/Compose 默认使用 Mock LLM：`LLM_PROVIDER=mock`、`LLM_ENABLE_REAL_API=false`。
- Demo 密码和 MySQL/Redis 密码只用于本地演示文档和 Compose 默认值，不代表生产配置。
- 第 8/9/10 轮业务成果未删除；AI/ML/RAG/LLM 仍只生成审批辅助建议，最终 `APPROVED` / `REJECTED` 仍必须走人工审批接口。
