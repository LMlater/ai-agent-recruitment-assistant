# API Walkthrough

## Round 16: 正式前端与批量 AI 检测

正式前端 `frontend-service` 不新增后端批量 AI Review 接口。上传 CSV 后，前端从 `POST /api/loan-applications/batch-import` 返回的 `imported[].applicationId` 中取得申请 ID，并按顺序调用已有单笔接口：

```text
POST /api/loan-applications/{applicationId}/ai-review
```

每条检测完成后，后端仍保存 AI report 和 Agent logs；前端再展示 Agent Trace、Tool Calls、Policy References 和人工审批操作。该流程避免真实 LLM 并发调用导致限流。

## Round 15.1: CSV fixture 上传说明

仓库内置 `docs/sample_import/loan_applications_sample.csv` 是脱敏批量申请 fixture。可视化 demo 的主流程是用户在页面手动选择该文件上传；后端只解析用户上传的 CSV，不提供绕过上传的样例导入接口。

## 批量导入脱敏申请

登录后可以下载 CSV 模板：

```powershell
curl.exe -L "$base/api/loan-applications/batch-import-template" `
  -H "Authorization: Bearer $token" `
  -o "loan_applications_template.csv"
```

CSV 表头必须保持为：

```text
applicant_name,id_card_masked,phone_masked,age,monthly_income,work_years,existing_debt,overdue_count,asset_proof_count,loan_amount,term_months,purpose
```

上传 CSV：

```powershell
curl.exe -s -X POST "$base/api/loan-applications/batch-import" `
  -H "Authorization: Bearer $token" `
  -F "file=@docs/sample_import/loan_applications_sample.csv"
```

返回结果会包含：

- `totalRows`：CSV 数据行总数。
- `successCount`：成功创建并提交的申请数。
- `failedCount`：失败行数。
- `imported`：成功导入的申请 ID、客户 ID、申请人脱敏信息、状态等。
- `errors`：逐行错误信息。

导入成功的申请会自动进入 `SUBMITTED`，可通过待审列表查询：

```powershell
curl.exe -s "$base/api/loan-applications?page=1&size=20" `
  -H "Authorization: Bearer $token"
```

安全边界：CSV 只能使用脱敏/模拟数据。完整身份证号、完整手机号会被拒绝；当前版本优先支持 CSV，`.xlsx` 请先另存为 CSV。

本文档用于面试演示 Java 后端 API 流程。示例使用 PowerShell `curl.exe`，demo admin 账号只用于本地演示，不可用于生产环境。所有最终审批都通过 `/api/approvals/...` 人工接口完成，AI review 不会直接把申请状态改成 `APPROVED` 或 `REJECTED`。

## 可视化页面入口

如果不想手敲下面的 `curl.exe` 命令，可以在两个服务启动后打开：

```text
http://localhost:8080/demo.html
```

这个页面按同样的 API 顺序执行：初始化/登录、创建客户、创建贷款申请、提交申请、触发 AI Review、查询 AI Reports、查询 Agent Logs、人工审批和查询审批历史。页面右下角 Raw JSON Panel 会展示最近一次接口响应，方便面试官直接看数据结构。

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

## 10. 人工 need-more-info 与补件复审

```powershell
curl.exe -s -X POST "$base/api/approvals/$applicationId/need-more-info" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"comment":"please provide additional repayment capacity proof"}'
```

进入 `NEED_MORE_INFO` 后，真实业务通常需要补件、重提和重新 AI review。第 10 轮实现了轻量闭环：

```powershell
curl.exe -s -X POST "$base/api/loan-applications/$applicationId/materials" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"materialSummary":"补充近 6 个月收入流水和资产证明摘要"}'

curl.exe -s "$base/api/loan-applications/$applicationId/material-updates" `
  -H "Authorization: Bearer $token"

curl.exe -s -X POST "$base/api/loan-applications/$applicationId/resubmit" `
  -H "Authorization: Bearer $token"

$review2 = curl.exe -s -X POST "$base/api/loan-applications/$applicationId/ai-review" `
  -H "Authorization: Bearer $token" | ConvertFrom-Json
```

补件内容只保存 mock 摘要，不上传真实身份证、手机号、征信报告或银行流水。重新 AI review 会新增一条 AI report，不覆盖旧报告；最终 approve/reject 仍走人工审批接口。

## 11. 查询审批历史

```powershell
curl.exe -s "$base/api/approvals/$applicationId/history" `
  -H "Authorization: Bearer $token"
```

审批历史和审计日志用于说明系统可追溯：AI 负责建议，人负责最终确认。
