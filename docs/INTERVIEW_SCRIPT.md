# Interview Script

## 30 秒项目介绍

我做的是一个基于 Spring Boot + FastAPI + LangGraph 的多 Agent 智能信贷审批辅助系统。Java 后端负责客户、贷款申请、AI 报告入库、Agent 日志和人工审批；Python 服务负责材料校验、规则与 ML 风险评分、制度 RAG 检索、合规检查和 LLM 报告生成。项目强调 AI 辅助、人工最终确认、日志审计和 fallback 稳定性。

## 2 分钟项目介绍

业务背景是信贷审批场景：传统系统需要录入客户信息、提交贷款申请、做风险评估、查制度依据，最后由审批人员确认结果。我把它拆成 Java 业务后端和 Python Agent 服务两个部分。

Java 后端用 Spring Boot + MyBatis，负责登录、客户、贷款申请、状态流转、AI review 触发、AI report 入库、Agent execution logs、人工审批和审计日志。Python 服务用 FastAPI + LangGraph，编排 IntakeAgent、RiskAgent、PolicyAgent、ComplianceAgent、DecisionAgent。

RiskAgent 结合规则评分和 Logistic Regression baseline；PolicyAgent 用本地制度 Markdown 做 TF-IDF RAG 检索；DecisionAgent 通过 LLM Provider 抽象生成报告，默认 Mock，可选 DashScope OpenAI-compatible，并保留 fallback。这个项目的边界是 AI/ML/RAG/LLM 只生成审批辅助建议，最终 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 必须走人工审批接口。工程亮点是双服务解耦、结构化合约、测试隔离、审计可追踪和演示脚本闭环。

## 常见 Q&A

### 1. 什么是 Agent？

在这个项目里，Agent 是围绕一个明确职责封装的审批节点，例如 IntakeAgent 做材料校验，RiskAgent 做风险评分，PolicyAgent 做制度检索。它不是简单聊天，而是接收结构化输入、执行确定任务、输出可被后续节点消费的结构化结果。

### 2. Agent 和普通 LLM 调用有什么区别？

普通 LLM 调用通常是一次 prompt 到一次 response。这个项目里的 Agent 有工作流状态、职责边界、日志、错误处理和结构化输出。LLM 只在 DecisionAgent 的报告生成阶段参与，而且不能改风险分数和最终审批状态。

### 3. 为什么信贷审批适合多 Agent？

信贷审批天然由多个步骤组成：材料校验、风险评分、制度引用、合规检查和审批建议。拆成多 Agent 后，每个环节更容易测试、解释和审计，也方便替换模型或检索模块。

### 4. 为什么不使用单 Agent？

单 Agent 容易把制度检索、风险评分和报告生成混在一起，难以定位错误。多 Agent 可以把规则、ML、RAG、LLM 的职责分开，任何一个节点失败时也更容易 fallback。

### 5. Supervisor / Router / Handoff 是什么？本项目有没有用？

Supervisor/Router/Handoff 是多 Agent 系统里常见的调度模式，分别用于统一调度、动态路由和任务交接。本项目当前使用固定顺序 LangGraph workflow，没有做复杂动态路由，因为面试版重点是可解释审批链路。后续可以在材料缺失、高风险或合规异常时加入 conditional edge。

### 6. LangChain 和 LangGraph 区别是什么？

LangChain 更偏 LLM、retriever、tool、prompt 等组件集成；LangGraph 更适合有状态、多节点、可观测的工作流编排。本项目用 LangGraph 编排审批流程，用 LangChain 生态作为后续 LLM/RAG 组件扩展方向。

### 7. 本项目为什么用 LangGraph？

审批流程不是一次性问答，而是多个节点串联并共享状态。LangGraph 能清楚表达节点、状态和边，后续可以加条件分支，也更容易把每个 Agent 的结果记录到日志。

### 8. Tool Calling 有什么风险？

风险包括调用未授权工具、参数被 prompt 注入污染、执行不可逆操作、把 LLM 输出直接当成业务决策。本项目没有让 LLM 直接调用审批写库工具，最终状态只能由 Java 人工审批接口写入。

### 9. RAG 怎么做的？

我把模拟制度 Markdown 按条款切分，提取 `R-001`、`P-003` 这类制度编号，用本地 TF-IDF + cosine similarity 检索，返回结构化 `policy_references`，包括制度编号、文档名、章节标题、内容和分数。

### 10. 怎么评估 RAG？

项目里有 `data/eval/rag_questions.jsonl`，包含问题、期望制度编号和期望文档。`evaluate_policy_retrieval.py` 会输出命中情况到 `rag_eval_results.json`，用于检查制度检索是否能找回预期条款。

### 11. 风控模型怎么做的？

使用公开 German Credit 数据集训练 Logistic Regression baseline，输出风险概率和模型等级。它不是生产风控模型，只是作为审批辅助信号，与规则评分融合。

### 12. ML 模型结果和规则评分冲突怎么办？

当前设计是规则评分为主、模型为辅，融合时保留规则原因和模型概率。如果模型不可用或异常，RiskAgent fallback 到规则评分，并在结果里记录 `model_used=false` 和错误信息。

### 13. LLM 会不会幻觉？怎么防？

会，所以我做了边界控制：LLM 只能基于已有 `risk_assessment` 和 `policy_references` 生成报告，保留 `allowed_policy_codes`，并校验不能引用未知制度编号。失败时回退到确定性报告。

### 14. 真实 LLM 超时怎么办？

真实 provider 调用失败或超时时，`ReportGenerationService` 会 fallback，不影响整个 Agent workflow。`decision_report_generation` 会记录 `llm_used`、`llm_provider` 和 `llm_error`，方便排查。

### 15. 为什么 AI 不能直接审批？

信贷审批涉及合规、责任归属和风险控制。这个项目明确把 AI 定位为辅助建议，最终 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 必须由人工审批接口确认，并留下审批记录和审计日志。

### 16. Java 后端和 Python Agent 怎么通信？

Java 后端通过 HTTP 调用 FastAPI `/api/v1/reviews`，发送客户和贷款申请结构化数据。Python 返回 `workflow_id`、风险结果、Agent results 和 report；Java 保存 AI report 和 Agent logs。

### 17. 如何保证审计和可追溯？

Java 侧保存 AI decision report、每个 Agent execution log、人工 approval record 和 audit log。报告里保留结构化制度引用，日志里保留 Agent 状态、耗时、摘要和 LLM 生成元信息。

### 18. 离真实银行生产系统还有哪些差距？

差距包括真实数据治理、模型验证、权限体系、风控策略引擎、灰度发布、监控告警、合规模型评审、向量库和真实制度库接入。这个项目是公开数据 + 模拟制度 + 工程验证的面试展示版，不包装成真实生产风控系统。

## 简短收尾

这个项目的价值不在于“让大模型自动放贷”，而在于把 Java 后端工程、AI Agent 编排、规则/ML/RAG/LLM 结合、fallback、安全边界和审计留痕串成一个可运行、可解释、可演示的闭环。
