# Iteration Log

## 无 Docker 启动文档修正

- README 和 `docs/TROUBLESHOOTING.md` 补充“无 Docker 本地源码启动方式”，明确 Docker 不是必须项，只是工程化交付加分项。
- 无 Docker 模式要求本地安装 MySQL 8、Redis、Java 17、Maven、Python 3.11，创建 `smart_credit_multi_agent` 数据库和 `smartcredit` 用户，并导入 `backend-service/src/main/resources/db/schema.sql`。
- 保留 Docker 模式，但标注为有 Docker 的机器可选；演示入口仍为 `http://localhost:8080/demo.html`。
- 本轮只做启动文档修正，不新增业务功能，不改代码逻辑。

## 第 13 轮：发布前验收、CI 手动触发与最终验收清单

- CI 增加 `workflow_dispatch`，GitHub Actions 页面可以手动 Run workflow；push/PR 触发逻辑继续保留。
- CI 将最终交付检查收口到 `delivery-package` job，在 `agent-service` 和 `backend-service` 通过后执行 `docker compose config` 与 `python scripts/check_demo_readiness.py --skip-services`。
- 新增 `docs/FINAL_ACCEPTANCE_CHECKLIST.md`，按功能验收、工程验收、安全边界验收、面试验收和当前已知限制整理最终发布前核对项。
- 更新 `docs/VALIDATION_LOG.md`，如实记录本地 Python、Backend、readiness、full demo stack 和 Docker CLI 验证结果。
- 本轮不新增业务功能，不修改审批状态机、Agent 主流程或数据库业务表。
- 当前项目进入冻结交付状态，后续只建议修实际 CI/Docker/演示问题，或根据投递反馈调整 README/简历表达。

## 第 12 轮：最终交付 Polish、故障排查与演示脚本

- README 顶部增加 CI badge、项目定位、Docker/源码最快启动方式、面试 Demo 7 步流程和不能夸大的边界说明。
- 新增 `docs/TROUBLESHOOTING.md`，覆盖 Docker 未安装、端口占用、MySQL 初始化、Agent/Backend 不可达、GitHub Actions badge、Windows Maven AccessDenied、Mock/真实 LLM 和 Demo 操作失败。
- 新增 `docs/FINAL_DEMO_SCRIPT.md`，提供 3 分钟和 5 分钟演示脚本，以及 Java/Python 拆分、Tool calling、RAG、ML baseline、人工审批边界、Docker/CI 等追问回答。
- 更新 `docs/FINAL_INTERVIEW_DELIVERY.md` 和 `docs/DEMO_GUIDE.md`，将 troubleshooting、最终 demo script 和启动路径串起来。
- `scripts/run_full_demo_stack.py` 增加 `static_ok`、Docker unavailable 友好提示和源码模式 fallback 命令。
- 本轮不新增业务功能，不修改第 8/9/10/11 轮核心逻辑；重点是最终面试交付收口。

## 第 10 轮：补件复审轻量闭环与面试交付收口

- Java `LoanStatus` 新增 `MATERIAL_UPDATED`、`RESUBMITTED`，实现 `NEED_MORE_INFO -> MATERIAL_UPDATED -> RESUBMITTED -> AI_REVIEWED` 复审状态流。
- 新增 `material_update_record` 表、`MaterialUpdateRecord` 实体和 `MaterialUpdateRecordMapper`，补件只保存本地 mock 摘要，不保存真实敏感材料。
- 新增 `POST /api/loan-applications/{id}/materials`、`POST /api/loan-applications/{id}/resubmit`、`GET /api/loan-applications/{id}/material-updates`。
- `AgentReviewService` 允许 `RESUBMITTED` 重新 AI review，完成后统一回到 `AI_REVIEWED`；`MATERIAL_UPDATED` 和 `NEED_MORE_INFO` 不能直接 AI review。
- `ApprovalService` 保持 approve/reject 只能从 `AI_REVIEWED` 进入；`SUBMITTED`、`RESUBMITTED`、`AI_REVIEWED` 可 need-more-info，`MATERIAL_UPDATED` 不允许人工审批跳转。
- Demo 页面支持演示 AI Review、人工 Need More Info、补件、重新提交、再次 AI Review 和最终人工 Approve/Reject。
- 文档新增最终面试交付文档，更新 README、架构、API、面试 Q&A、复评设计、恢复说明和简历表达。
- 本轮不接入真实银行数据，不提交 `.env`、真实 API Key 或真实客户材料，普通测试继续使用 Mock LLM。

## 第 9 轮：Tool Trace 端到端、高风险 Senior Review 与复评设计

- Java `AgentReviewService` 在不修改数据库表结构的前提下，将 `AgentResult.result.tool_calls` 追加为 `agent_execution_log.output_summary` 短摘要，并继续保留 `decision_report_generation` 的 `llm_used`、`llm_provider`、`llm_error`。
- Demo 页面在 Agent Logs 时间线展示每个 Agent 的工具调用明细：工具名、中文说明、状态、耗时、输入摘要、输出摘要和失败错误；无工具调用时展示空状态。
- Python LangGraph 新增 `route_after_risk`：高风险进入 `SeniorReviewAgent`，低/中风险走普通分支；材料缺失分支继续跳过 RiskAgent 和 SeniorReviewAgent。
- 新增 `SeniorReviewAgent` 和 `SeniorReviewChecklistTool`，只生成高级人工复核要求，不修改风险评分、不写最终审批状态、不允许 AI 自动 approve/reject/need-more-info。
- ComplianceAgent 和 DecisionAgent 会把 senior manual review 要求写入合规提示与决策理由，便于面试解释“高风险需要更严格人工复核”。
- 新增 `docs/REASSESSMENT_FLOW_DESIGN.md`，说明真实业务补件、重提、重评、材料快照、审计日志和旧 AI 报告保留方案。
- 本轮继续使用 Mock LLM 普通测试，不接入真实银行数据，不提交 `.env` 或真实 API Key，不修改数据库 schema。
- 验证：Python `tests/test_reviews_api.py` 通过；Java `AgentReviewServiceTest` 和 `DemoPageStaticTest` 通过。

## 第 8 轮：Tool System、条件分支与审批状态机强化

- Python `agent-service` 新增 `app/tools/` 显式工具层：材料校验、规则评分、模型信号、制度检索、合规护栏和报告生成均通过工具执行。
- 每个成功执行的 Agent 都会在 `AgentResult.result.tool_calls` 中返回工具调用记录，包括 tool name、状态、输入/输出摘要、开始/结束时间、耗时和错误信息。
- LangGraph workflow 从固定线性流程升级为条件路由：材料缺失时跳过 RiskAgent，写入 `risk_skipped=true`、`risk_score=0`、`risk_level=HIGH`、`suggested_amount=0`，并由 DecisionAgent 输出 `NEED_MORE_INFO`。
- Java `ApprovalService` 收紧人工审批状态机：approve/reject 只允许 `AI_REVIEWED`；need-more-info 只允许 `SUBMITTED` 或 `AI_REVIEWED`；`DRAFT` 和终态不能直接或重复人工审批。
- Demo 页面保留本地快捷演示能力，但文案改为“生成一笔脱敏演示申请”，并明确真实业务中客户和贷款申请来自业务系统，演示按钮只是 seed/mock fixture。
- 本轮不接入真实银行数据，不提交 `.env`、真实 API Key 或真实客户信息，不让 LLM 调用写库工具，也不让 AI 自动完成最终审批。
- 验证：`agent-service` 全量 pytest 通过；`backend-service` Maven 测试通过。

## 可视化 Demo 页面

- 新增 `backend-service/src/main/resources/static/demo.html`，访问地址为 `http://localhost:8080/demo.html`，用于本地面试展示完整信贷审批辅助流程。
- 页面使用原生 HTML + CSS + JavaScript，不引入 Vue、React、npm 或前端构建工具。
- 页面提供服务状态检查、demo admin 初始化/登录、脱敏客户创建、贷款申请创建、提交、AI Review、AI Reports、Agent Logs、人工审批和审批历史查询。
- 页面展示 Loan Application、AI Review Summary、Policy References、Agent Logs、Manual Approval 和 Raw JSON，方便面试官直接看结构化返回。
- 面试展示版将页面拆成 `客户申请端` 与 `银行审批工作台` 两个 Tab，并新增“一键准备演示数据”按钮，自动完成 init admin、login、create customer、create loan application 和 submit application。
- 银行审批工作台新增顶部 LLM Provider 状态、LLM Used/Error 卡片、Agent 日志时间线、中文摘要翻译 `translateSummary(text)`，以及默认折叠的 Raw JSON Panel。
- 页面手动验证已跑通完整闭环：AI Summary 展示 `risk_level=LOW`、`risk_score=100`、`ai_report_id=8`；Policy References 展示 `R-004`、`M-003`、`P-002`、`P-003`、`P-004`；5 个 Agent 均为 `SUCCESS`，DecisionAgent 使用 `mock` LLM 且 `llm_error=null`；人工 Approve 后审批历史显示 `AI_REVIEWED -> APPROVED`。
- 轻量优化 `demo.html`：AI Review 成功后 Loan Application Card 显示 `AI_REVIEWED`；人工 Approve/Reject/Need More Info 成功后显示最终状态、自动刷新审批历史、禁用三个人工审批按钮，并提示重新演示需准备新的演示申请。
- 新增轻量静态页面测试，确认 demo 页面存在并保留关键接口钩子。
- 本轮不修改数据库表结构，不改 AI review 主业务逻辑，不让 AI 自动审批最终状态，不提交 `.env`、MySQL 密码或 API Key。

## 真实双服务 E2E 联调验证

- 本地 `agent-service` 与 `backend-service` 均已启动并通过 readiness 检查，`ok=true`，backend/agent 均 reachable。
- `python scripts/run_e2e_credit_review_demo.py` 已跑通真实 Java + Python 双服务链路，`application_id=5`，`ai_report_id=3`，`agent_log_count=5`，`decision_agent_llm_provider=mock`。
- `python scripts/run_e2e_credit_review_demo.py --application-id 5 --manual-decision approve` 已跑通人工审批演示，`manual_decision_status=APPROVED`。
- 本次联调使用 mock LLM，未调用真实百炼；AI review 只产生 `final_decision_from_ai` 辅助建议，最终 `APPROVED` 由人工审批接口完成。
- 本次只更新文档记录，未提交 MySQL 密码、API Key、`.env` 或本地配置文件，未修改业务代码或数据库表结构。

## 第 6 轮：演示包装与面试交付版完善

- 新增 `docs/DEMO_GUIDE.md`，整理项目一句话介绍、本地演示顺序、E2E 输出字段解释和常见问题。
- 完善 `docs/ARCHITECTURE.md`，加入 Mermaid 总体架构图、Java/Python 职责边界、双服务原因、LangGraph 选型原因和审批边界。
- 新增 `docs/API_WALKTHROUGH.md`，提供 admin 初始化、客户创建、贷款申请、AI review、报告/日志查询和人工审批 API 演示流程。
- 新增 `docs/INTERVIEW_SCRIPT.md`，提供 30 秒介绍、2 分钟介绍和围绕本项目的 Agent/RAG/ML/LLM/审计边界 Q&A。
- 新增 `scripts/check_demo_readiness.py` 和 `agent-service/tests/test_check_demo_readiness.py`，用标准库检查关键文件、服务可达性和 `.env` 是否被 git 跟踪。
- 更新 README、子服务 README、简历材料和恢复文档，明确本项目是公开数据 + 模拟制度 + 工程验证，不是真实银行生产风控系统。
- 本轮未提交 `.env` 或真实 API Key，未调用真实百炼，未修改数据库表结构，未让 AI 自动审批最终状态。

## 第 5 轮：端到端演示闭环

- 新增 `scripts/run_e2e_credit_review_demo.py`，通过 Java 后端 HTTP API 串起创建或复用贷款申请、触发 Python Agent 审核、查询 AI 报告、查询 Agent 执行日志，以及可选人工最终审批。
- Java 后端继续支持结构化 `policy_references`，并增强 Python `/api/v1/reviews` 返回中 `AgentResult.result.decision_report_generation` 的合约测试。
- `AgentReviewService` 在不修改数据库表结构的前提下，将 DecisionAgent 的 `llm_used`、`llm_provider`、`llm_error` 摘要写入现有 `agent_execution_log.output_summary`。
- AI review 后贷款申请只更新为 `AI_REVIEWED`；最终 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 仍必须由人工审批接口确认。
- 普通 `agent-service` 测试仍通过 `tests/conftest.py` 强制 Mock LLM，不调用真实百炼；真实 API 只允许本地显式 smoke/demo。
- 本轮未提交 `.env` 或真实 API Key，未改 Java 数据库表结构，未删除 MockLLMClient、fallback、RAG、ML 或规则评分代码。

## 第 1 轮：双服务骨架与 Mock 多 Agent 工作流初始化

- 初始化 Spring Boot backend-service。
- 初始化 FastAPI + LangGraph agent-service。
- 建立客户、贷款申请、AI 审批报告、Agent 执行日志、人工审批、审计日志基础结构。
- 添加 Mock 风控评分、Mock 制度检索和多 Agent 工作流测试。

## 第 1.5 轮：工程修复与演示链路完善

- 收紧 AI review 状态边界：首次执行要求 `SUBMITTED`，允许 `AI_REVIEWED` 为演示或复评再次执行，拒绝 `DRAFT`、`APPROVED`、`REJECTED`、`NEED_MORE_INFO`。
- 收紧普通状态更新接口：`PATCH /api/loan-applications/{id}/status` 不能设置 `APPROVED`、`REJECTED`、`NEED_MORE_INFO`，最终决策必须走人工审批接口并保留审批记录。
- 新增 AI 报告查询接口：`GET /api/loan-applications/{id}/ai-reports`、`GET /api/ai-reports/{reportId}`。
- 新增 Agent 执行日志查询接口：`GET /api/loan-applications/{id}/agent-logs`、`GET /api/agent-workflows/{workflowId}/logs`。
- 补充低、中、高风险 seed 贷款申请，仍为 Mock 数据，不使用真实客户信息。
- 强化 Python Agent 测试：覆盖低、中、高风险、材料缺失、全 Agent 输出完整性。
- 强化 Java 单元测试：覆盖 AI review 状态边界、普通状态更新边界、AI 报告和 Agent 日志查询服务。
- 改进全局异常处理：业务异常保留可读消息，参数校验返回字段信息，系统异常只返回通用错误并记录堆栈。
- 更新根 README 与 backend-service README，补全从初始化管理员到人工审批历史查询的本地演示 curl 流程。

## 第 2 轮第一段：公开信贷数据与风控模型 baseline

- 新增 German Credit 数据下载脚本：`agent-service/scripts/download_german_credit.py`。
- 新增数据清洗和字段映射脚本：`agent-service/scripts/prepare_credit_dataset.py`。
- 生成 `data/processed/credit_cases.csv`、`train.csv`、`test.csv`。
- 新增 Logistic Regression baseline 训练脚本：`agent-service/scripts/train_risk_model.py`。
- 输出模型评估指标：accuracy、precision、recall、F1、ROC-AUC、confusion matrix。
- 保存模型 artifact：`agent-service/models/credit_risk_model.joblib` 和 `model_metadata.json`。
- 新增 `RiskModelService`，可加载模型并输出结构化风险概率、标签、版本、特征和解释。
- 生成低、中、高风险覆盖的模拟 seed SQL 和模型评估案例。
- 当前模型尚未接入 `RiskAgent`，下一轮计划接入为“规则评分 + ML 模型评分”组合。

## 第 2 轮第二段：RiskAgent 接入 ML baseline

- `RiskAgent` 新增规则评分 + Logistic Regression baseline 概率融合，保留原有规则扣分原因。
- `risk_assessment` 现在输出规则分、规则等级、模型概率、模型等级、模型解释、融合分、融合等级、建议额度、`model_used` 和 `model_error`。
- 模型不可用、加载失败、特征缺失或预测异常时，自动降级为纯规则评分，AgentResult 仍保持 `SUCCESS`。
- `DecisionAgent` 增强模型信号解释，明确模型概率、模型等级和模型版本，或说明规则 fallback。
- `ComplianceAgent` 增加“模型输出只是辅助信号，必须结合规则原因和制度引用复核”的合规提示。
- 新增 RiskAgent 融合单元测试、FastAPI review 融合字段断言、RiskModelService 三档阈值和缺失特征测试。
- 本轮未接入 RAG、未接入真实 LLM、未修改 Java 后端表结构。

## 第 3 轮第一段：制度 RAG baseline

- 新增 `PolicyDocumentLoader`，将模拟制度 Markdown 按条款切分为稳定 chunk，并提取制度编号。
- 新增 `PolicyRetrievalService`，使用本地 `TfidfVectorizer` + cosine similarity 检索制度依据，不接入外部 Embedding API、Chroma、FAISS 或真实 LLM。
- 新增结构化 `PolicyReference` schema，`ReviewReport.policy_references` 从 `list[str]` 升级为结构化 JSON 对象。
- 增强 `PolicyAgent` 查询构造，纳入申请用途、金额、风险等级、规则原因、模型信号、缺失材料、合规提示、DTI、逾期、人工复核和 AI/ML 边界词。
- 重写四份模拟制度文档为 `P-001`、`M-001`、`R-001`、`C-001` 等条款结构。
- 新增 `data/eval/rag_questions.jsonl`、`agent-service/scripts/evaluate_policy_retrieval.py`、生成 `data/eval/rag_eval_results.json`，并新增 `docs/RAG_DESIGN.md`。
- 本轮仍不使用真实银行制度、真实客户敏感数据、真实 LLM、外部向量库或自动审批，也不修改 Java 后端表结构。

## 第 3.1 轮：RAG 结构化引用与 Java 后端兼容性修复

- Java 后端新增 `PolicyReference` DTO，`ReviewReport.policyReferences` 支持 Python `policy_references` 返回的结构化对象。
- 新增 `AgentReviewResponseJsonTest`，覆盖 Jackson 反序列化结构化 `policy_references`、`agent_results` 和 `risk_assessment`。
- 更新 `AgentReviewServiceTest`，确认 `objectMapper.writeValueAsString(response.getReport())` 保存 `report_json` 时仍保留结构化制度引用。
- 清理 `data/eval/rag_eval_results.json` metadata 中的本地绝对路径，改为仓库相对路径。
- 补充 `data/eval/rag_questions.jsonl` 的 `expected_documents`，并在评估结果 case 中保留该字段。
- 本轮未接入真实 LLM，未调用阿里云百炼，未读取 API Key，未修改数据库表结构。

## 第 4 轮第一段：LLM Provider 抽象与百炼兼容客户端

- 新增 `LLMClient` 抽象层，`DecisionAgent` 通过 `ReportGenerationService` 调用可替换的报告生成客户端。
- 新增 `MockLLMClient`，默认用于本地开发、普通单元测试和无 API Key 场景。
- 新增 `OpenAICompatibleLLMClient`，支持通过环境变量配置阿里云百炼 OpenAI-compatible chat completions。
- `agent-service/.env` 可由 `python-dotenv` 自动加载，且系统环境变量优先，`.env` 继续保持不提交。
- `DecisionAgent` 可基于规则评分、ML 模型信号和 RAG 制度引用生成更自然的审批辅助报告，但不改变 `final_decision`、`risk_score` 或 `risk_level`。
- LLM 返回非 JSON、引用未知制度编号或调用异常时，会 fallback 到确定性报告文本，Agent 工作流保持稳定。
- 单元测试不依赖真实 API；真实 DashScope smoke test 默认 skip，只有本地显式配置 `DASHSCOPE_API_KEY` 和 `LLM_ENABLE_REAL_API=true` 才运行。
- 未提交真实 API Key，未要求用户在提示词中提供 API Key，未修改 Java 数据库表结构。

## 第 4 轮第二段：LLM 端到端演示、测试隔离与真实百炼调用保护

- 新增 `tests/conftest.py`，普通 pytest 默认强制 `LLM_PROVIDER=mock`、`LLM_ENABLE_REAL_API=false`，避免本地 `.env` 让普通测试误调用真实百炼。
- 保留 `test_dashscope_live_smoke.py` 作为单独运行的真实 API smoke test，并增强 key/base URL/enable flag skip 条件和异常脱敏检查。
- 新增 `scripts/run_llm_review_demo.py`，可用 Mock 或真实百炼跑端到端 review demo，输出 workflow、风险、制度编号和 `decision_report_generation` 元信息。
- 新增 demo 与测试隔离相关单元测试；FastAPI review 测试确认 DecisionAgent 的 `result` 中可见 `decision_report_generation`。
- 本轮未提交 `.env` 或真实 API Key，未修改 Java 数据库表结构，未允许 LLM 改最终审批状态。

## 第 4 轮第三段：真实 LLM demo 稳定化

- `scripts/run_llm_review_demo.py` 新增 `--mock`、`--real`、`--compact` 参数，分别支持稳定 Mock 展示、真实百炼尝试和短上下文演示。
- `--real` 在用户未设置时使用 demo 默认 `LLM_TIMEOUT_SECONDS=90`、`LLM_MAX_TOKENS=600`，但不覆盖用户已有配置。
- LLM prompt payload 现在压缩 `policy_references` 和 `risk_assessment`，减少真实模型超时概率，同时保留 `allowed_policy_codes` 与未知制度编号校验。
- demo 输出新增 `demo_mode`、`llm_timeout_seconds`、`llm_max_tokens`，仍不输出 API Key。
- 普通测试仍通过 pytest 隔离强制 Mock，不调用真实百炼；真实 LLM 超时 fallback 作为保护机制保留。
# 第 11 轮：CI + Docker Compose 一键交付 + 最终工程包装

- 新增 GitHub Actions CI：push/pull_request 到 `main` 时分别运行 `agent-service` Python 3.11 测试、`backend-service` Java 17 Maven 测试，并在两者通过后运行 readiness 静态检查。
- 新增 `agent-service/Dockerfile`：Python 3.11 slim，默认 Mock LLM，不复制 `.env`，暴露 8001 并运行 Uvicorn。
- 新增 `backend-service/Dockerfile`：Maven 3.9 + Temurin 17 多阶段构建，JRE 运行，使用 `MYSQL_URL`、`MYSQL_USER`、`MYSQL_PASSWORD`、`REDIS_HOST`、`REDIS_PORT`、`AGENT_SERVICE_BASE_URL`、`JWT_SECRET` 环境变量。
- 扩展 `docker-compose.yml`：保留 MySQL/Redis 和初始化 SQL 挂载，新增健康检查、`agent-service`、`backend-service`，默认 Mock LLM，支持 `docker compose up --build` 启动完整本地演示栈。
- 新增 `.dockerignore`：避免 `.env`、缓存、构建产物和日志进入镜像上下文。
- 新增 `scripts/run_full_demo_stack.py`：标准库实现，支持 `--check-only`，检查 Docker、Dockerfile、Compose 服务和 readiness，并输出演示命令与 URL。
- 增强 `scripts/check_demo_readiness.py`：检查 CI workflow、两个 Dockerfile、完整 Compose 四服务和最终交付文档，`--skip-services` 不要求本地服务已启动。
- 更新 README、Demo Guide、Architecture、Final Interview Delivery、Resume Notes、Conversation Recovery、Validation Log，补齐 CI/Docker/Compose/readiness 的面试讲法。
- 未新增业务能力，未删除第 8/9/10 轮成果；Tool Trace、SeniorReviewAgent、补件复审状态机和人工最终审批边界保持不变。
