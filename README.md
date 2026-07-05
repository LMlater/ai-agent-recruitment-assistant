# SmartCreditMultiAgent

[![CI](https://github.com/LMlater/ai-agent-recruitment-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/LMlater/ai-agent-recruitment-assistant/actions/workflows/ci.yml)

## Round 15.1: Clarify Project CSV Fixture Upload Flow

仓库内置 `docs/sample_import/loan_applications_sample.csv` 作为脱敏批量申请样例。面试演示时，用户从本地仓库目录选择该 CSV 上传，系统解析文件后创建待审申请队列。下载模板只是辅助入口，不代表系统绕过上传自动生成申请。

正确流程：

```text
打开 demo 页面 -> 登录 demo admin -> 在批量导入区域点击选择文件
-> 选择 docs/sample_import/loan_applications_sample.csv
-> 点击“上传 CSV 导入” -> 查看待审申请列表 -> 触发 AI预审
```

本项目没有自动导入内置样例的专用接口或按钮；CSV 导入必须经过浏览器文件上传流程。

## 第 15 轮：批量导入与中文审批工作台

本轮让 Demo 更接近真实信贷业务入口：客户和贷款申请可以从脱敏 CSV 批量导入。页面保留低/高风险快速演示按钮，但它们只作为面试快捷样例，不再是唯一入口。

- 新增 `GET /api/loan-applications/batch-import-template` 下载 CSV 模板。
- 新增 `POST /api/loan-applications/batch-import` 上传 CSV，逐行创建 `Customer` 和 `LoanApplication`，并自动提交为 `SUBMITTED`。
- CSV 字段为 `applicant_name,id_card_masked,phone_masked,age,monthly_income,work_years,existing_debt,overdue_count,asset_proof_count,loan_amount,term_months,purpose`。
- 导入会拒绝完整身份证号、完整手机号等敏感明文；单行失败会记录到导入结果，不阻断其他合法行。
- 当前版本优先支持 CSV；`.xlsx` 会返回明确提示：请先另存为 CSV，Excel 模板作为后续增强。
- Demo 页新增“批量导入脱敏申请”“待审申请列表”“人工通过 / 人工拒绝 / 要求补件”等中文化审批工作台能力。
- 示例文件见 `docs/sample_import/loan_applications_sample.csv`。

SmartCreditMultiAgent 是一个面向 Java 后端/金融科技/AI Agent 工程面试的信贷审批辅助项目。

它不是普通 CRUD，也不是简单 ChatBot，而是把 Spring Boot 业务后端、FastAPI + LangGraph 多 Agent、Tool Calling、风控规则 + ML baseline、制度 RAG、LLM 报告生成、补件复审、人工审批和审计留痕串成一个可演示闭环。

## 最快启动

Docker 不是必须项，只是工程化交付加分项；没有 Docker 的机器可以使用本地 MySQL 8 + Redis 的源码模式完成演示。

有 Docker 的机器可选 Docker 模式：

```bash
python scripts/run_full_demo_stack.py --check-only
docker compose up --build
```

访问：

```text
Demo page: http://localhost:8080/demo.html
Agent health: http://localhost:8001/health
```

无 Docker 模式：

前置依赖：

- MySQL 8
- Redis
- Java 17
- Maven
- Python 3.11

初始化本地 MySQL：

```sql
CREATE DATABASE IF NOT EXISTS smart_credit_multi_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'smartcredit'@'localhost' IDENTIFIED BY 'smartcredit_dev_password';
GRANT ALL PRIVILEGES ON smart_credit_multi_agent.* TO 'smartcredit'@'localhost';
FLUSH PRIVILEGES;
```

导入表结构：

```bash
mysql -usmartcredit -psmartcredit_dev_password smart_credit_multi_agent < backend-service/src/main/resources/db/schema.sql
```

启动本地 Redis 后，启动 agent-service：

```bash
cd agent-service
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

另开终端启动 backend-service：

```bash
cd backend-service
mvn spring-boot:run
```

访问：

```text
http://localhost:8080/demo.html
```

## 面试 Demo 流程 7 步

1. 生成一笔脱敏演示申请。
2. 触发 AI Review。
3. 查看风险评分、制度引用、Agent Logs、Tool Calls。
4. 高风险时观察 SeniorReviewAgent 分支。
5. 人工选择 Need More Info。
6. 提交补件摘要并重新提交，再次 AI Review。
7. 人工 Approve / Reject，查看审批历史和审计留痕。

提示：面试现场可以使用真实 DashScope/OpenAI-compatible LLM 生成报告，但真实 LLM 可能需要 30-90 秒。等待时可讲解 Agent Trace、Tool Trace、Policy RAG 和 human-in-the-loop 边界；LLM 只生成审批辅助报告，不拥有最终审批写库权限。本机 Redis 当前不是核心 demo 主链路强依赖，无 Redis 时仍可先启动 backend-service 验证主流程。

## 不能夸大的边界

- 不是真实银行生产系统。
- 不接真实银行数据。
- 不自动放贷。
- ML 模型是 baseline，不是生产级风控模型。
- RAG 使用模拟制度库。
- Demo 补件只保存摘要，不上传真实敏感材料。
- Docker 默认密码只用于本地 demo。
- 默认 Mock LLM，不要求真实 DashScope/百炼/OpenAI API。

## 最终交付文档

- 故障排查手册：[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- 最终演示脚本：[docs/FINAL_DEMO_SCRIPT.md](docs/FINAL_DEMO_SCRIPT.md)
- 最终面试交付：[docs/FINAL_INTERVIEW_DELIVERY.md](docs/FINAL_INTERVIEW_DELIVERY.md)
- 演示指南：[docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md)

## 发布前验收

最终验收入口见 [docs/FINAL_ACCEPTANCE_CHECKLIST.md](docs/FINAL_ACCEPTANCE_CHECKLIST.md)。提交后请到 GitHub Actions 页面确认 CI 实际运行结果；本仓库的 workflow 支持 push/PR 自动触发，也支持手动 Run workflow。

本地可先运行：

```bash
python scripts/check_demo_readiness.py --skip-services
python scripts/run_full_demo_stack.py --check-only
```

如果当前机器安装了 Docker CLI，可选运行：

```bash
docker compose config
docker compose up --build
```

## 第 11 轮：面试演示最快启动方式

本轮补齐 CI + Docker Compose + 一键演示栈交付。默认使用 Mock LLM，不需要真实 API Key；不要提交 `.env`。下面的 demo admin 密码和 MySQL/Redis 密码只用于本地演示，不代表生产配置。

无 Docker 模式：

```bash
python scripts/check_demo_readiness.py --skip-services
cd agent-service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

```bash
cd backend-service
mvn spring-boot:run
```

有 Docker 的机器可选 Docker 模式：

```bash
python scripts/run_full_demo_stack.py --check-only
docker compose up --build
```

访问地址：

```text
Agent health: http://localhost:8001/health
Demo page: http://localhost:8080/demo.html
```

CI 会在 GitHub Actions 中分别运行 `agent-service` 的 `python -m pytest tests -q`、`backend-service` 的 `mvn test`，并在两个测试任务通过后执行 `python scripts/check_demo_readiness.py --skip-services`。

## 快速演示入口

本项目为公开数据 + 模拟制度 + 工程验证的信贷审批辅助系统，不是真实银行生产风控系统。AI/ML/RAG/LLM 只生成审批辅助建议，最终审批必须由人工接口确认。

- 演示总指南：[docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md)
- 架构图与职责边界：[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- API 演示流程：[docs/API_WALKTHROUGH.md](docs/API_WALKTHROUGH.md)
- 面试讲解稿：[docs/INTERVIEW_SCRIPT.md](docs/INTERVIEW_SCRIPT.md)
- 最终面试交付：[docs/FINAL_INTERVIEW_DELIVERY.md](docs/FINAL_INTERVIEW_DELIVERY.md)
- 简历要点：[docs/RESUME_NOTES.md](docs/RESUME_NOTES.md)
- 验证日志：[docs/VALIDATION_LOG.md](docs/VALIDATION_LOG.md)

常用命令：

```bash
cd agent-service
python -m pytest tests -q
python scripts/run_llm_review_demo.py --mock
```

```bash
cd backend-service
mvn test
```

```bash
python scripts/check_demo_readiness.py
python scripts/run_e2e_credit_review_demo.py --application-id 1
```

可视化 Demo 页面：

```text
http://localhost:8080/demo.html
```

面试演示顺序：先启动 `agent-service`，再启动 `backend-service`，打开 `demo.html`。页面分为“客户申请端”和“银行审批工作台”：先点击“生成一笔脱敏演示申请”创建本地 seed/mock fixture，再到银行审批工作台触发 AI Review、查看风险评分、制度引用、Agent 工具调用时间线和 LLM 信息，最后通过人工审批接口确认最终状态。真实业务中客户和贷款申请来自业务系统，不由 Agent 自动生成。

安全说明：不要提交 `.env` 或真实 API Key；demo admin 默认账号密码只用于本地演示。

## 第 10 轮：补件复审轻量闭环与面试交付收口

- Java 状态机新增 `MATERIAL_UPDATED`、`RESUBMITTED`，落地完整复审流：`NEED_MORE_INFO -> MATERIAL_UPDATED -> RESUBMITTED -> AI_REVIEWED`。
- 新增 `POST /api/loan-applications/{id}/materials`、`POST /api/loan-applications/{id}/resubmit` 和 `GET /api/loan-applications/{id}/material-updates`，补件只保存 mock 摘要，不上传真实材料。
- 补件和重提都会写 audit log；每次重新 AI Review 都新增 AI report，不覆盖旧报告。
- Demo 页面支持演示 `AI Review -> Need More Info -> 补件 -> 重新提交 -> 再次 AI Review -> 人工 Approve/Reject`。
- 最终 `APPROVED` / `REJECTED` 仍必须由 Java 人工审批接口确认，LLM 不拥有最终审批写库能力。

## 第 9 轮：Tool Trace 端到端与高风险 Senior Review 分支

- Python `agent-service` 在 RiskAgent 后新增高风险条件路由：`HIGH` 风险进入 `SeniorReviewAgent -> PolicyAgent -> ComplianceAgent -> DecisionAgent`，低/中风险仍走普通分支，材料缺失分支仍跳过 RiskAgent 和 SeniorReviewAgent。
- `SeniorReviewAgent` 只生成高级人工复核要求，不修改 `risk_score`、`risk_level` 或最终数据库审批状态；AI/ML/RAG/LLM 仍只给审批辅助建议。
- Java `AgentReviewService` 在不改表结构的前提下，把 `tool_calls` 短摘要追加到 `agent_execution_log.output_summary`，并保留 `decision_report_generation` 元信息。
- Demo 页面在 Agent Logs 时间线中展示工具名、状态、耗时、输入/输出摘要和失败错误；优先使用最新 AI Review 返回的结构化 `agent_results[].result.tool_calls`。
- 新增 `docs/REASSESSMENT_FLOW_DESIGN.md`，说明真实业务补件后应重新 AI review、保留旧报告、记录材料更新和重提审计日志，最终审批仍必须走人工接口。

## 第 8 轮：Tool System、条件分支与审批状态机强化

- Python `agent-service` 新增显式 tool 层：材料校验、规则评分、模型信号、制度检索、合规护栏和报告生成都通过工具执行，并在 `AgentResult.result.tool_calls` 中保留 trace。
- LangGraph 从固定线性流程升级为条件路由：材料缺失时跳过 RiskAgent，写入 `risk_skipped=true` 和保守默认风险值，直接进入制度检索、合规检查和补件建议。
- Java 人工审批状态机收紧：approve/reject 只能从 `AI_REVIEWED` 进入，need-more-info 只能从 `SUBMITTED` 或 `AI_REVIEWED` 进入，终态不能重复审批。
- Demo 页面区分真实业务流程和本地面试演示快捷入口，避免误解为真实业务中“一键生成客户和申请”。

## 第 5 轮：端到端演示闭环

本轮新增项目级脚本 `scripts/run_e2e_credit_review_demo.py`，用于通过 Java 后端 HTTP API 串起创建或复用贷款申请、触发 Python Agent 审核、查询 AI 报告、查询 Agent 执行日志，以及可选执行人工最终审批。

启动服务：

```bash
cd agent-service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

```bash
cd backend-service
mvn spring-boot:run
```

运行普通测试：

```bash
cd agent-service
python -m pytest tests -q
```

```bash
cd backend-service
mvn test
```

运行 Agent 独立 demo：

```bash
cd agent-service
python scripts/run_llm_review_demo.py --mock
python scripts/run_llm_review_demo.py --compact
```

运行 Java + Python 端到端 demo：

```bash
python scripts/run_e2e_credit_review_demo.py
python scripts/run_e2e_credit_review_demo.py --application-id 1
python scripts/run_e2e_credit_review_demo.py --application-id 1 --manual-decision approve
```

打开本地可视化 Demo 页面：

```text
http://localhost:8080/demo.html
```

新版页面面向面试展示做了业务化整理：顶部展示 backend/agent/LLM 状态，客户申请端负责准备演示申请，银行审批工作台负责 AI Review、AI Report、Agent Logs、人工审批和审批历史。Raw JSON 面板默认折叠，只在需要向面试官展示接口结构时展开。

`BACKEND_BASE_URL` 可用于覆盖默认后端地址 `http://localhost:8080`。默认演示建议使用 Mock LLM；真实百炼只在本地显式配置并由 agent-service 启用时才会被调用。AI/ML/RAG/LLM 只生成审批辅助建议，最终 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 必须由人工审批接口确认，系统会保存 AI 报告、Agent 执行日志和审计记录。不要提交 `.env` 或真实 API Key。

基于 Spring Boot + FastAPI + LangGraph 的多 Agent 智能信贷审批辅助系统。

这个仓库用于展示一个“Java 后端业务系统 + Python 多 Agent 审批服务”的双服务工程项目。第一轮目标不是接入真实银行数据或真实大模型，而是跑通信贷审批辅助系统的核心工程闭环：客户、贷款申请、AI 审批建议、Agent 执行日志、人工审批、审计留痕和项目文档。

## 项目架构

```text
backend-service  -> Spring Boot 3 + MyBatis + MySQL + Redis + JWT
agent-service    -> FastAPI + LangGraph + Mock RAG/LLM 扩展点
MySQL/Redis      -> docker-compose 本地基础设施
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

无 Docker 模式下，请本地安装并启动 MySQL 8 与 Redis。MySQL 默认库名为 `smart_credit_multi_agent`，本地 demo 用户为 `smartcredit`，密码为 `smartcredit_dev_password`。初始化 SQL 位于 `backend-service/src/main/resources/db/schema.sql`。

```sql
CREATE DATABASE IF NOT EXISTS smart_credit_multi_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'smartcredit'@'localhost' IDENTIFIED BY 'smartcredit_dev_password';
GRANT ALL PRIVILEGES ON smart_credit_multi_agent.* TO 'smartcredit'@'localhost';
FLUSH PRIVILEGES;
```

```bash
mysql -usmartcredit -psmartcredit_dev_password smart_credit_multi_agent < backend-service/src/main/resources/db/schema.sql
```

有 Docker 的机器也可以可选使用：

```bash
docker compose up -d mysql redis
```

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
- LangGraph 条件工作流：IntakeAgent 后按材料完整性路由，材料缺失时跳过 RiskAgent，否则执行 RiskAgent -> PolicyAgent -> ComplianceAgent -> DecisionAgent。
- 三档规则风控评分测试：LOW、MEDIUM、HIGH。
- Mock 制度文档和 RetrievalService 预留。

## Mock 说明

- RiskAgent 使用规则评分 + Logistic Regression 基线模型概率融合，模型只作为辅助信号。
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

## 第 2 轮数据与模型基线

本轮引入 UCI German Credit / Statlog German Credit 公开数据集，完成下载、清洗映射、Logistic Regression 基线模型训练、模型评估、模型文件保存和模拟 seed SQL 生成。第 2 轮第二段已将模型接入 `RiskAgent`，形成“规则评分 + ML 模型概率”的融合评估；模型仍只作为审批辅助信号，不自动审批。

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

当前基线模型指标：accuracy 0.6000、precision 0.3936、recall 0.6167、F1 0.4805、ROC-AUC 0.6787。详见 `docs/MODEL_BASELINE.md`。

第 2 轮第二段输出的 `risk_assessment` 同时包含 `rule_score`、`rule_level`、`rule_reasons`、`model_risk_probability`、`model_risk_level`、`model_explanation`、`model_used`、`model_error`、融合后的 `risk_score` 和 `risk_level`。如果模型文件不可用，Agent 会降级为纯规则评分并保持 AgentResult 为 `SUCCESS`。

## 第 3 轮第一段：制度 RAG 基线

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
python -m pytest tests -q
```

普通测试会通过 `tests/conftest.py` 强制使用 Mock LLM，不会调用百炼，即使本地 `.env` 开启了真实 API。

真实百炼 smoke test 仅在本地配置 `agent-service/.env` 或环境变量后，直接指定 smoke 文件手动运行；如果系统环境变量和 `.env` 同时存在，系统环境变量优先：

```bash
python -m pytest tests/test_dashscope_live_smoke.py -q
```

本地 `.env` 示例：

```env
LLM_PROVIDER=dashscope
LLM_ENABLE_REAL_API=true
DASHSCOPE_API_KEY=your-key
DASHSCOPE_BASE_URL=your-base-url
DASHSCOPE_MODEL=qwen3.7-plus
```

LLM review demo：

```bash
python scripts/run_llm_review_demo.py --mock
python scripts/run_llm_review_demo.py --real
python scripts/run_llm_review_demo.py --compact
```

`--mock` 用于稳定展示，不调用百炼；`--real` 使用本地百炼配置，可能受网络和模型响应影响；`--compact` 使用更短上下文和较小生成参数，更适合真实模型演示。真实 LLM 超时时会触发 fallback，这是预期保护机制，不是系统崩溃。

配置方式和安全边界见 `docs/LLM_INTEGRATION.md`。仓库只提交 `.env.example` 占位符，不提交真实 API Key。
