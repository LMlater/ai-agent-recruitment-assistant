# backend-service

这是 SmartCreditMultiAgent 的 Spring Boot 后端服务，负责登录/JWT、客户管理、贷款申请、Java 调 Python AI review、AI report 入库、Agent execution logs、人工审批和审计日志。

## 面试演示材料入口

准备面试演示时，优先从仓库根目录的交付文档开始看：

- `../docs/DEMO_GUIDE.md`
- `../docs/ARCHITECTURE.md`
- `../docs/API_WALKTHROUGH.md`
- `../docs/INTERVIEW_SCRIPT.md`
- `../docs/VALIDATION_LOG.md`

从仓库根目录运行 readiness 检查：

```bash
python scripts/check_demo_readiness.py
```

这个后端服务仍然是最终人工审批状态的写入入口。AI review 可以保存报告和日志，但最终 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 必须通过 `/api/approvals/{applicationId}/...` 人工审批接口写入。

## 启动服务

1. 从仓库根目录启动 MySQL 和 Redis：

```bash
docker compose up -d mysql redis
```

2. 启动 Python agent-service，端口为 8001。

3. 启动当前 Java 后端服务：

```bash
mvn spring-boot:run
```

Swagger UI 地址为 `http://localhost:8080/swagger-ui.html`。

## 首次请求

当用户表为空时，初始化管理员账号：

```bash
curl -X POST http://localhost:8080/api/auth/init-admin \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"Admin@123456\",\"displayName\":\"Admin\"}"
```

登录：

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"Admin@123456\"}"
```

后续受保护接口使用返回的 JWT，格式为 `Authorization: Bearer <token>`。

## 核心流程

1. 通过 `/api/customers` 创建脱敏客户。
2. 通过 `/api/loan-applications` 创建贷款申请。
3. 通过 `/api/loan-applications/{id}/submit` 提交申请。
4. 通过 `/api/loan-applications/{id}/ai-review` 执行 AI 审批辅助。
5. 通过 `/api/approvals/{applicationId}/approve`、`/reject` 或 `/need-more-info` 执行最终人工审批。

## 本地演示流程

下面示例使用 PowerShell + `curl.exe`。AI review 可以在 `SUBMITTED` 状态执行；为了演示复评，也允许在 `AI_REVIEWED` 状态再次执行。最终审批状态必须走人工审批 API，不能通过 `PATCH /api/loan-applications/{id}/status` 直接设置。

```powershell
$base = "http://localhost:8080"

curl.exe -s -X POST "$base/api/auth/init-admin" `
  -H "Content-Type: application/json" `
  -d '{"username":"admin","password":"Admin@123456","displayName":"Admin"}'

$login = curl.exe -s -X POST "$base/api/auth/login" `
  -H "Content-Type: application/json" `
  -d '{"username":"admin","password":"Admin@123456"}' | ConvertFrom-Json
$token = $login.data.token

$customer = curl.exe -s -X POST "$base/api/customers" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"name":"Demo Medium Risk Customer","idCardMasked":"4401********2036","phoneMasked":"138****2036","age":29,"monthlyIncome":8500,"workYears":3,"existingDebt":65000,"overdueCount":1,"assetProofCount":1}' | ConvertFrom-Json
$customerId = $customer.data.id

$loan = curl.exe -s -X POST "$base/api/loan-applications" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d "{`"customerId`":$customerId,`"amount`":130000,`"termMonths`":24,`"purpose`":`"home appliance upgrade`"}" | ConvertFrom-Json
$applicationId = $loan.data.id

curl.exe -s -X POST "$base/api/loan-applications/$applicationId/submit" `
  -H "Authorization: Bearer $token"

$review = curl.exe -s -X POST "$base/api/loan-applications/$applicationId/ai-review" `
  -H "Authorization: Bearer $token" | ConvertFrom-Json
$workflowId = $review.data.workflow_id

$reports = curl.exe -s "$base/api/loan-applications/$applicationId/ai-reports" `
  -H "Authorization: Bearer $token" | ConvertFrom-Json
$reportId = $reports.data[0].id

curl.exe -s "$base/api/ai-reports/$reportId" `
  -H "Authorization: Bearer $token"

curl.exe -s "$base/api/loan-applications/$applicationId/agent-logs" `
  -H "Authorization: Bearer $token"

curl.exe -s "$base/api/agent-workflows/$workflowId/logs" `
  -H "Authorization: Bearer $token"

curl.exe -s -X POST "$base/api/approvals/$applicationId/approve" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"comment":"manual approval after checking AI report and agent logs"}'

curl.exe -s "$base/api/approvals/$applicationId/history" `
  -H "Authorization: Bearer $token"
```

其它人工最终决策示例：

```powershell
curl.exe -s -X POST "$base/api/approvals/$applicationId/reject" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"comment":"manual rejection after checking AI report and agent logs"}'

curl.exe -s -X POST "$base/api/approvals/$applicationId/need-more-info" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"comment":"please provide additional repayment capacity proof"}'
```

## 第 5 轮：端到端 demo

项目级脚本 `../scripts/run_e2e_credit_review_demo.py` 会通过 HTTP 调用当前后端服务。后端再调用 `agent-service`，保存 AI decision report 和 Agent execution logs，并把贷款申请保持在 `AI_REVIEWED`，直到人工审批 API 被调用。

先启动两个服务：

```bash
cd agent-service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

```bash
cd backend-service
mvn spring-boot:run
```

从仓库根目录运行 E2E demo：

```bash
python scripts/run_e2e_credit_review_demo.py
python scripts/run_e2e_credit_review_demo.py --application-id 1
python scripts/run_e2e_credit_review_demo.py --application-id 1 --manual-decision approve
```

如果后端地址不是默认值，可以通过 `BACKEND_BASE_URL` 覆盖。脚本不会读取或打印 DashScope/百炼密钥；是否使用真实 LLM 只由已经启动的 `agent-service` 配置决定。`DecisionAgent.result.decision_report_generation` 会保留在 Java 响应合约中，并摘要写入 `agent_execution_log.output_summary`，不需要修改数据库表结构。
