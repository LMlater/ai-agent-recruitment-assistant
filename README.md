# SmartCreditMultiAgent

基于 Spring Boot + FastAPI + LangGraph 的多 Agent 智能信贷审批辅助系统。

这个仓库用于展示一个“Java 后端业务系统 + Python 多 Agent 审批服务”的双服务工程项目。第一轮目标不是接入真实银行数据或真实大模型，而是跑通信贷审批辅助系统的核心工程闭环：客户、贷款申请、AI 审批建议、Agent 执行日志、人工审批、审计留痕和项目文档。

## 项目架构

```text
backend-service  -> Spring Boot 3 + MyBatis + MySQL + Redis + JWT
agent-service    -> FastAPI + LangGraph + Mock RAG/LLM extension points
MySQL/Redis      -> docker-compose local infrastructure
```

核心原则：AI 只生成审批辅助建议，不自动做最终通过或拒绝。最终状态 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 必须通过人工审批接口写入，并保留审批记录和审计日志。

## 目录结构

```text
docs/                       架构、接口、数据、迭代和恢复上下文文档
backend-service/            Java 信贷业务系统
agent-service/              Python 多 Agent 审批服务
data/                       后续公开数据集、清洗数据和评估集占位
docker-compose.yml          MySQL 8 + Redis
PROJECT_CONTEXT.md          长期项目上下文
```

## 启动 MySQL 和 Redis

```bash
docker compose up -d mysql redis
```

MySQL 默认库名为 `smart_credit_multi_agent`。初始化 SQL 位于 `backend-service/src/main/resources/db/`。

## 启动 agent-service

```bash
cd agent-service
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

测试：

```bash
pytest tests -q
```

## 启动 backend-service

```bash
cd backend-service
mvn spring-boot:run
```

Swagger UI:

```text
http://localhost:8080/swagger-ui.html
```

## 核心业务流程

1. 初始化管理员账号：`POST /api/auth/init-admin`
2. 登录并获取 JWT：`POST /api/auth/login`
3. 创建脱敏客户：`POST /api/customers`
4. 创建贷款申请：`POST /api/loan-applications`
5. 提交贷款申请：`POST /api/loan-applications/{id}/submit`
6. 执行 AI 审批辅助：`POST /api/loan-applications/{id}/ai-review`
7. 人工审批通过、拒绝或补充材料：`POST /api/approvals/{applicationId}/approve|reject|need-more-info`

## 示例 AI 审批请求

```bash
curl -X POST http://localhost:8001/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d "{\"application_id\":1,\"customer\":{\"id\":1,\"age\":32,\"monthly_income\":12000,\"work_years\":5,\"existing_debt\":30000,\"overdue_count\":0,\"asset_proof_count\":2},\"loan_application\":{\"amount\":80000,\"term_months\":24,\"purpose\":\"personal consumption\"}}"
```

## 当前已实现

- Spring Boot 后端分层：auth、customer、loan、agent review、approval、audit。
- MyBatis mapper、schema.sql、data.sql。
- JWT 登录和当前用户接口。
- Java 调 Python Agent 服务并保存 AI 报告、Agent 日志、审计日志。
- FastAPI `POST /api/v1/reviews`。
- LangGraph 固定顺序工作流：IntakeAgent -> RiskAgent -> PolicyAgent -> ComplianceAgent -> DecisionAgent。
- 三档规则风控评分测试：LOW、MEDIUM、HIGH。
- Mock 制度文档和 RetrievalService 预留。

## Mock 说明

- RiskAgent 使用规则评分 + Logistic Regression baseline 模型概率融合，模型只作为辅助信号。
- PolicyAgent 使用本地 Markdown 关键词检索，不是向量库 RAG。
- DecisionAgent 输出审批建议，不代表自动审批。
- 当前 seed 数据是模拟数据，不包含真实身份证、手机号或银行客户信息。

## 后续计划

1. 接入公开信贷数据集并训练简单风控分类模型。
2. 接入 Chroma/FAISS，构建制度文档 RAG。
3. 接入真实 LLM，生成带制度引用的审批报告。
4. 增加端到端集成测试、Dockerfile、评估报告和简历包装材料。

## 第 1.5 轮本地演示流程

以下命令以 PowerShell + `curl.exe` 为例。AI 审批只允许在 `SUBMITTED` 状态首次执行；为了演示复评，`AI_REVIEWED` 状态允许再次执行 AI review；最终 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 必须走人工审批接口，不能通过普通状态更新接口设置。

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
  -d '{"name":"Demo Low Risk Customer","idCardMasked":"4401********2026","phoneMasked":"139****2026","age":32,"monthlyIncome":12000,"workYears":6,"existingDebt":20000,"overdueCount":0,"assetProofCount":3}' | ConvertFrom-Json
$customerId = $customer.data.id

$loan = curl.exe -s -X POST "$base/api/loan-applications" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d "{`"customerId`":$customerId,`"amount`":80000,`"termMonths`":24,`"purpose`":`"personal consumption`"}" | ConvertFrom-Json
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
  -d '{"comment":"manual approval after AI-assisted review"}'

curl.exe -s "$base/api/approvals/$applicationId/history" `
  -H "Authorization: Bearer $token"
```

人工审批还支持以下两个互斥决策，演示时请选择其一，不要在同一笔申请上连续执行多个最终动作：

```powershell
curl.exe -s -X POST "$base/api/approvals/$applicationId/reject" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"comment":"manual rejection after AI-assisted review"}'

curl.exe -s -X POST "$base/api/approvals/$applicationId/need-more-info" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"comment":"please provide additional income proof"}'
```

## 第 2 轮数据与模型 baseline

本轮引入 UCI German Credit / Statlog German Credit 公开数据集，完成下载、清洗映射、Logistic Regression baseline 训练、模型评估、模型 artifact 保存和模拟 seed SQL 生成。第 2 轮第二段已将模型接入 `RiskAgent`，形成“规则评分 + ML 模型概率”的融合评估；模型仍只作为审批辅助信号，不自动审批。

运行命令：

```bash
cd agent-service
python scripts/download_german_credit.py
python scripts/prepare_credit_dataset.py
python scripts/train_risk_model.py
pytest tests -q
```

主要产物：

- 原始公开数据：`data/raw/german_credit/german.data`、`data/raw/german_credit/german.doc`
- 清洗数据：`data/processed/credit_cases.csv`、`data/processed/train.csv`、`data/processed/test.csv`
- 模型文件：`agent-service/models/credit_risk_model.joblib`
- 模型元信息：`agent-service/models/model_metadata.json`
- 评估指标：`data/eval/model_metrics.json`
- 评估案例：`data/eval/model_eval_cases.jsonl`
- 模拟 seed SQL：`data/seed/generated_customers_seed.sql`、`data/seed/generated_loan_applications_seed.sql`

当前 baseline 指标：accuracy 0.6000、precision 0.3936、recall 0.6167、F1 0.4805、ROC-AUC 0.6787。详见 `docs/MODEL_BASELINE.md`。

第 2 轮第二段输出的 `risk_assessment` 同时包含 `rule_score`、`rule_level`、`rule_reasons`、`model_risk_probability`、`model_risk_level`、`model_explanation`、`model_used`、`model_error`、融合后的 `risk_score` 和 `risk_level`。如果模型 artifact 不可用，Agent 会降级为纯规则评分并保持 AgentResult 为 `SUCCESS`。

## 第 3 轮第一段：制度 RAG baseline

本轮将 `PolicyAgent` 从本地 Markdown 关键词检索升级为可测试、可解释、可引用来源的本地制度检索：

- `PolicyDocumentLoader` 将 `agent-service/knowledge_base/*.md` 按 `##` 条款切分，并提取 `P-001`、`M-001`、`R-001`、`C-001` 等条款编号。
- `PolicyRetrievalService` 使用本地 `TfidfVectorizer` + cosine similarity，不使用外部 Embedding API、Chroma、FAISS、真实 LLM API 或真实银行制度。
- `/api/v1/reviews` 的 `report.policy_references` 现在是结构化 JSON，包含 `policy_code`、`document_name`、`section_title`、`content`、`score`。
- RAG 评估集为 `data/eval/rag_questions.jsonl`，评估结果由 `agent-service/scripts/evaluate_policy_retrieval.py` 生成到 `data/eval/rag_eval_results.json`。

运行：

```bash
cd agent-service
python scripts/evaluate_policy_retrieval.py
pytest tests -q
```

设计边界见 `docs/RAG_DESIGN.md`。AI、ML 和 RAG 均只作为审批辅助依据，最终审批仍必须走人工审批链路。

## 第 4 轮第一段：LLM Provider 抽象

本轮在 `agent-service` 中新增可替换的 LLM Provider 抽象，默认使用 `MockLLMClient`，并预留 OpenAI-compatible 客户端用于本地按需接入阿里云百炼。LLM 只负责基于规则评分、ML 模型信号和 RAG 制度引用组织审批辅助报告文本，不改变 `final_decision`、`risk_score` 或 `risk_level`，也不绕过人工审批。

普通测试不需要 API Key：

```bash
cd agent-service
pytest tests -q
```

真实百炼 smoke test 仅在本地配置 `agent-service/.env` 或环境变量后手动运行，默认会跳过；如果系统环境变量和 `.env` 同时存在，系统环境变量优先：

```bash
LLM_ENABLE_REAL_API=true pytest tests/test_dashscope_live_smoke.py -q
```

配置方式和安全边界见 `docs/LLM_INTEGRATION.md`。仓库只提交 `.env.example` 占位符，不提交真实 API Key。
