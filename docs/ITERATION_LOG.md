# Iteration Log

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
