# API Walkthrough

本文档用于面试演示 Java 后端 API 流程。示例使用 PowerShell `curl.exe`，demo admin 账号只用于本地演示，不可用于生产环境。所有最终审批都通过 `/api/approvals/...` 人工接口完成，AI review 不会直接把申请状态改成 `APPROVED` 或 `REJECTED`。

## 1. 初始化并登录 admin

```powershell
$base = "http://localhost:8080"

curl.exe -s -X POST "$base/api/auth/init-admin" `
  -H "Content-Type: application/json" `
  -d '{"username":"admin","password":"Admin@123456","displayName":"Demo Admin"}'

$login = curl.exe -s -X POST "$base/api/auth/login" `
  -H "Content-Type: application/json" `
  -d '{"username":"admin","password":"Admin@123456"}' | ConvertFrom-Json
$token = $login.data.token
```

## 2. 创建脱敏客户

```powershell
$customer = curl.exe -s -X POST "$base/api/customers" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"name":"Demo Customer","idCardMasked":"4401********2099","phoneMasked":"138****2099","age":32,"monthlyIncome":12000,"workYears":5,"existingDebt":30000,"overdueCount":0,"assetProofCount":2}' | ConvertFrom-Json
$customerId = $customer.data.id
```

## 3. 创建贷款申请

```powershell
$loan = curl.exe -s -X POST "$base/api/loan-applications" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d "{`"customerId`":$customerId,`"amount`":80000,`"termMonths`":24,`"purpose`":`"interview demo loan`"}" | ConvertFrom-Json
$applicationId = $loan.data.id
```

## 4. 提交申请

```powershell
curl.exe -s -X POST "$base/api/loan-applications/$applicationId/submit" `
  -H "Authorization: Bearer $token"
```

## 5. 触发 AI review

```powershell
$review = curl.exe -s -X POST "$base/api/loan-applications/$applicationId/ai-review" `
  -H "Authorization: Bearer $token" | ConvertFrom-Json
$workflowId = $review.data.workflow_id
```

关注字段：

- `final_decision`：AI 建议，不是最终审批结果。
- `risk_score` / `risk_level`：规则评分和 ML baseline 的融合结果。
- `report.policy_references`：RAG 检索到的结构化制度引用。
- `agent_results[].result.decision_report_generation`：DecisionAgent 的 LLM provider/fallback 元信息。

## 6. 查询 AI reports

```powershell
$reports = curl.exe -s "$base/api/loan-applications/$applicationId/ai-reports" `
  -H "Authorization: Bearer $token" | ConvertFrom-Json
$reportId = $reports.data[0].id

curl.exe -s "$base/api/ai-reports/$reportId" `
  -H "Authorization: Bearer $token"
```

`report_json` 会保留结构化 `policy_references`、`risk_assessment`、`decision_reasons` 和合规提示。

## 7. 查询 Agent logs

```powershell
curl.exe -s "$base/api/loan-applications/$applicationId/agent-logs" `
  -H "Authorization: Bearer $token"

curl.exe -s "$base/api/agent-workflows/$workflowId/logs" `
  -H "Authorization: Bearer $token"
```

日志中可以看到 IntakeAgent、RiskAgent、PolicyAgent、ComplianceAgent、DecisionAgent 的状态、耗时和摘要。DecisionAgent 的 `decision_report_generation` 元信息会摘要到 `output_summary`。

## 8. 人工 approve

```powershell
curl.exe -s -X POST "$base/api/approvals/$applicationId/approve" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"comment":"manual approval after checking AI report and agent logs"}'
```

## 9. 人工 reject

```powershell
curl.exe -s -X POST "$base/api/approvals/$applicationId/reject" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"comment":"manual rejection after checking AI report and agent logs"}'
```

## 10. 人工 need-more-info

```powershell
curl.exe -s -X POST "$base/api/approvals/$applicationId/need-more-info" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"comment":"please provide additional repayment capacity proof"}'
```

同一笔申请演示时只选择一种最终人工动作，避免连续覆盖最终状态。

## 11. 查询审批历史

```powershell
curl.exe -s "$base/api/approvals/$applicationId/history" `
  -H "Authorization: Bearer $token"
```

审批历史和审计日志用于说明系统可追溯：AI 负责建议，人负责最终确认。
