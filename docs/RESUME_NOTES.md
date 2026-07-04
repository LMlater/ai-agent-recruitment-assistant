# Resume Notes

## 第 8 轮后简历描述

### 项目名称

基于 Spring Boot 与 LangGraph 的多 Agent 智能信贷审批辅助系统

### 一句话项目描述

基于 Spring Boot + FastAPI + LangGraph 构建信贷审批辅助系统，融合 tool calling、规则评分、ML baseline、制度 RAG 检索和 LLM 报告生成，实现 AI 审批建议、tool trace、条件路由、报告入库、审计留痕和人工最终审批闭环。

### Java 后端方向 bullet

- 基于 Spring Boot + MyBatis 设计客户、贷款申请、AI 审批报告、Agent 执行日志、人工审批记录和审计日志等核心模块，提供 REST API 支撑本地演示闭环。
- 实现贷款申请状态机边界：AI review 仅能将申请推进到 `AI_REVIEWED`；approve/reject 只允许从 `AI_REVIEWED` 进入，补件只允许从 `SUBMITTED` 或 `AI_REVIEWED` 进入。
- 对接 Python FastAPI Agent 服务，反序列化结构化 `policy_references` 和 `decision_report_generation`，并将 AI report 与 Agent execution logs 持久化。
- 编写 Java 单元测试覆盖 AI review 状态边界、结构化 DTO 合约、报告 JSON 保存和 Agent 日志保存，提升 Java/Python 双服务接口稳定性。

### AI Agent 方向 bullet

- 基于 FastAPI + LangGraph 编排 IntakeAgent、RiskAgent、PolicyAgent、ComplianceAgent、DecisionAgent，形成基于 tool calling 的多 Agent 审批辅助工作流。
- 设计 `MaterialChecklistTool`、`RiskRuleTool`、`RiskModelTool`、`PolicySearchTool`、`ComplianceGuardrailTool`、`ReportGenerationTool`，每个 Agent 输出 `tool_calls` trace。
- 使用 LangGraph conditional routing：材料缺失时跳过 RiskAgent，返回 `risk_skipped=true` 和补件建议，避免无效输入进入风控计算。
- RiskAgent 融合规则评分与 Logistic Regression baseline，模型不可用时 fallback 到规则评分，并保留 `model_used`、风险概率和解释字段。
- PolicyAgent 基于本地 Markdown 制度库实现 TF-IDF RAG 检索，返回结构化制度引用并提供评估集验证检索命中情况。
- DecisionAgent 通过 LLM Provider 抽象支持 MockLLM 和 DashScope OpenAI-compatible 客户端，真实调用失败时 fallback，且不允许 LLM 改最终审批状态。

### 银行科技岗位方向 bullet

- 围绕信贷审批辅助场景设计“AI 建议 + 人工复核”闭环，强调风险评分、制度引用、合规提示和审批留痕。
- 强调 human-in-the-loop：LLM 只能生成报告文本，不调用写库工具，不自动完成贷款审批。
- 将 RAG 检索到的制度条款编号、风险评分原因、模型辅助信号写入审批报告，提升审批建议可解释性。
- 通过 AI report、Agent execution logs、approval record 和 audit log 保留关键链路证据，便于事后追踪和面试演示。
- 明确系统边界：公开数据 + 模拟制度 + 工程验证，不接入真实银行生产数据，不让 AI 自动完成贷款审批。

### 不建议写的夸大表述

- 不要写“真实银行风控模型”。
- 不要写“接入银行生产数据”。
- 不要写“自动完成贷款审批”。
- 不要写“达到生产级准确率”。
- 不要写“替代人工审批员”。

- 第 5 轮新增根目录 `scripts/run_e2e_credit_review_demo.py`，用于面试演示 Java backend-service + Python agent-service 的端到端闭环。
- 端到端脚本输出 `application_id`、`workflow_id`、AI 建议、风险结果、`ai_report_id`、Agent 日志数量、DecisionAgent LLM provider、policy codes 和 `manual_approval_required=true`。
- 脚本默认不执行最终审批；如需演示人工最终确认，使用 `--manual-decision approve|reject|need-more-info`，最终状态仍由 Java 人工审批接口写入。
- `AgentReviewService` 现在会把 `decision_report_generation` 的 `llm_used`、`llm_provider`、`llm_error` 摘要追加到现有 Agent 日志 `output_summary`，没有修改数据库表结构。
- 后端测试覆盖 Python 返回的结构化 `policy_references`、`AgentResult.result.decision_report_generation`、AI report 保存和 AI review 状态边界。
- 普通测试仍使用 Mock LLM，不读也不调用真实百炼；`.env` 和真实 API Key 不得提交。

- Java + Python 双服务架构：Spring Boot 负责业务系统，FastAPI 负责 AI 审批辅助服务。
- LangGraph 多 Agent 工作流：IntakeAgent、RiskAgent、PolicyAgent、ComplianceAgent、DecisionAgent。
- 信贷审批业务流程：客户建档、贷款申请、AI 审批建议、人工审批、审计留痕。
- 风控评分：基于逾期次数、负债收入比、工作年限、申请额度、资产证明的规则评分。
- 制度检索预留：第一轮关键词检索，后续可替换为 Chroma/FAISS RAG。
- Agent 执行日志：每个 Agent 保留输入摘要、输出摘要、耗时和状态。
- 人工审批与审计留痕：AI 只给建议，最终审批必须人工确认。
- 第 1.5 轮工程修复：AI review 只允许 `SUBMITTED` 首次执行，`AI_REVIEWED` 仅用于演示/复评重跑；`APPROVED`、`REJECTED`、`NEED_MORE_INFO` 必须通过人工审批接口进入。
- 第 1.5 轮新增查询链路：AI 报告可通过申请 ID 或报告 ID 查询，Agent 执行日志可通过申请 ID 或 workflow ID 查询。
- 本地演示入口：根 README 与 `backend-service/README.md` 已补充 PowerShell `curl.exe` 流程，包含 init-admin、login、create customer、create loan、submit、AI review、report/log 查询、manual approval、approval history。
- 第 2 轮第一段：基于 UCI German Credit 公开信贷数据集构建风控样本，清洗映射为项目字段，训练 Logistic Regression baseline。
- 模型评估输出 accuracy、precision、recall、F1、ROC-AUC 和混淆矩阵；当前 ROC-AUC 为 0.6787，F1 为 0.4805，Recall 为 0.6167。
- 风控模型只用于审批辅助信号，不做自动决策；第 2 轮第二段已接入 RiskAgent 并与规则评分融合。
- 简历亮点表达：公开数据处理 + 特征映射 + baseline 模型训练 + 模型评估 + artifact 管理 + 审批辅助边界。
- 第 2 轮第二段：RiskAgent 已采用规则评分 + Logistic Regression baseline 概率融合，输出规则原因、模型概率、模型等级、融合风险分和融合风险等级。
- 模型不可用时会降级为规则评分，`risk_assessment` 记录 `model_used=false` 和 `model_error`，避免 AI review 主链路失败。
- DecisionAgent 和 ComplianceAgent 会说明模型只是审批辅助信号，不自动审批，最终审批仍走人工审批接口。
- 第 3 轮第一段已加入本地制度 RAG baseline：`PolicyDocumentLoader`、`PolicyRetrievalService`、结构化 `PolicyReference`、增强版 `PolicyAgent`、条款化模拟制度文档、RAG 评估集/结果和 `docs/RAG_DESIGN.md`。
- `/api/v1/reviews` 现在返回结构化 `policy_references`；Java 后端可继续按 JSON 字符串保存 AI report，不需要改数据库表结构。
- 当前 RAG 仅使用本地 `scikit-learn` TF-IDF + cosine similarity，不使用真实 LLM API、外部 Embedding、Chroma、FAISS、真实银行制度或敏感数据。
- 设计可替换 LLM Provider 抽象，支持 Mock 与 OpenAI-compatible 模型服务。
- 通过 RAG 制度引用、规则评分和模型信号生成审批辅助报告。
- 实现 LLM 调用失败 fallback，保障 Agent 工作流稳定。
- API Key 通过环境变量配置，避免密钥泄露；普通测试不依赖真实百炼 API，真实 smoke test 默认 skip。
- 普通 pytest 通过 `agent-service/tests/conftest.py` 强制 Mock LLM；真实百炼 smoke test 需要直接运行 `python -m pytest tests/test_dashscope_live_smoke.py -q`。
- `agent-service/scripts/run_llm_review_demo.py` 可运行端到端 LLM review demo，`LLM_ENABLE_REAL_API=false` 用 Mock，配置完整且为 `true` 时用百炼。
- LLM review demo 支持 `--mock`、`--real`、`--compact`；`--compact` 和真实模式会使用短上下文/较小输出参数以降低超时概率，超时 fallback 属于预期保护机制。
