# backend-service

Spring Boot service for SmartCreditMultiAgent. It owns login/JWT, customer management, loan applications, Java-to-Python AI review calls, AI report persistence, agent execution logs, manual approval, and audit logs.

## Run

1. Start MySQL and Redis from the repository root:

```bash
docker compose up -d mysql redis
```

2. Start the Python agent service on port 8001.

3. Start this service:

```bash
mvn spring-boot:run
```

Swagger UI is available at `http://localhost:8080/swagger-ui.html`.

## First Requests

Initialize an administrator when the user table is empty:

```bash
curl -X POST http://localhost:8080/api/auth/init-admin \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"Admin@123456\",\"displayName\":\"Admin\"}"
```

Login:

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"Admin@123456\"}"
```

Use the returned JWT as `Authorization: Bearer <token>` for protected APIs.

## Core Flow

1. Create a masked customer under `/api/customers`.
2. Create a loan application under `/api/loan-applications`.
3. Submit it with `/api/loan-applications/{id}/submit`.
4. Run AI assistance with `/api/loan-applications/{id}/ai-review`.
5. Use `/api/approvals/{applicationId}/approve`, `/reject`, or `/need-more-info` for the final human decision.

## Local Demo Flow

PowerShell examples below use `curl.exe`. AI review is available for `SUBMITTED` applications, and can be re-run from `AI_REVIEWED` only for demo or reassessment. Final statuses must go through manual approval APIs instead of `PATCH /api/loan-applications/{id}/status`.

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

Alternative final human decisions:

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
