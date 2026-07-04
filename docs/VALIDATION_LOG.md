# Validation Log

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
