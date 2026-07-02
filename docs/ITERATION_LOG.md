# Iteration Log

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
