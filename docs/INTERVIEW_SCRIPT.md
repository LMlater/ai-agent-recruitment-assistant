# Interview Script

## 30 秒项目介绍

我做的是一个基于 Spring Boot + FastAPI + LangGraph 的多 Agent 智能信贷审批辅助系统。Java 后端负责客户、贷款申请、AI 报告入库、Agent 日志和人工审批；Python 服务负责材料校验、规则与 ML 风险评分、制度 RAG 检索、合规检查和 LLM 报告生成。第 8 轮加入了显式 Tool System、tool trace 和材料缺失条件路由，项目强调 AI 辅助、人工最终确认、日志审计和 fallback 稳定性。

## 2 分钟项目介绍

业务背景是信贷审批场景：传统系统需要录入客户信息、提交贷款申请、做风险评估、查制度依据，最后由审批人员确认结果。我把它拆成 Java 业务后端和 Python Agent 服务两个部分。

Java 后端用 Spring Boot + MyBatis，负责登录、客户、贷款申请、状态流转、AI review 触发、AI report 入库、Agent execution logs、人工审批和审计日志。Python 服务用 FastAPI + LangGraph，编排 IntakeAgent、RiskAgent、PolicyAgent、ComplianceAgent、DecisionAgent。

RiskAgent 结合规则评分和 Logistic Regression baseline；PolicyAgent 用本地制度 Markdown 做 TF-IDF RAG 检索；DecisionAgent 通过 LLM Provider 抽象生成报告，默认 Mock，可选 DashScope OpenAI-compatible，并保留 fallback。每个 Agent 会调用明确的工具，并把 `tool_calls` 返回给后端保存或展示。这个项目的边界是 AI/ML/RAG/LLM 只生成审批辅助建议，最终 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 必须走人工审批接口。工程亮点是双服务解耦、结构化合约、条件路由、测试隔离、审计可追踪和演示脚本闭环。

## 可视化演示话术

我会打开 `http://localhost:8080/demo.html` 做完整流程展示。这个页面不是生产前端，只是本地面试 Demo，用原生 HTML、CSS、JavaScript 调 Java 后端 API。真实业务中客户和贷款申请来自业务系统；页面里的“生成一笔脱敏演示申请”只是为了本地面试快速创建 seed/mock fixture。流程是先检查 backend 和 agent-service 状态，再初始化并登录 demo admin，创建脱敏客户和贷款申请，提交后触发 AI Review，然后查看 AI Report、RAG 制度引用和 Agent logs，最后点击人工 Approve、Reject 或 Need More Info 确认最终审批状态。

这里要强调两点：第一，页面中的 AI review 只展示 `final_decision_from_ai`、风险评分、制度引用和报告摘要；第二，最终 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 由人工审批接口写入，不是 LLM 或 Agent 自动改库。

## 常见 Q&A

### 0.1 如何证明 Agent 真的调用了工具？

每个 Agent 的结果里都有 `result.tool_calls`，记录工具名、状态、输入/输出摘要、开始/结束时间、耗时和错误信息。Java 后端保存 Agent log 时，会把工具短摘要追加到 `agent_execution_log.output_summary`，Demo 页面的 Agent Logs 时间线也会展示工具调用卡片。这样面试时可以从 Python 响应、Java 日志和页面三处证明 tool trace 是端到端可审计的。

### 0.2 高风险和普通风险流程有什么区别？

普通低/中风险路径是 `risk -> policy -> compliance -> decision`；高风险会在 RiskAgent 后进入 `SeniorReviewAgent`，生成 `senior_review_required=true` 和 senior review reasons，再进入制度检索、合规检查和决策建议。这个分支只增加人工高级复核要求，不改变风险分数，也不写最终审批状态。

### 0.3 Tool calling 的安全控制是什么？

本项目的 tool calling 是工程侧显式工具调用，不是让 LLM 自由选择并执行写库工具。工具只做材料检查、规则评分、模型信号、制度检索、合规提示、报告生成和高级复核清单；输入输出只保留摘要用于审计，不保存完整敏感输出。最终 approve/reject/need-more-info 仍只能通过 Java 人工审批接口写入。

### 0.4 为什么不让 LLM 调用最终审批工具？

信贷审批涉及合规、责任归属和审计追责。LLM 可以辅助组织报告和解释依据，但不能承担最终业务责任，也不应该拥有写入 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 的能力。本项目明确把 AI 输出定位为建议，最终状态必须由人工审批接口确认并留下 approval record 和 audit log。

### 0.5 真实业务里补件后怎么重新评估？

当前 Demo 中 `NEED_MORE_INFO` 作为终态足够展示边界；真实业务通常需要补件后重评。推荐引入 `MATERIAL_UPDATED`、`RESUBMITTED` 等状态，补件记录进入材料快照或更新表，重提后重新触发 AI Review，旧 AI 报告不覆盖，新旧报告都可追溯，最终审批仍由人工完成。详细设计见 `docs/REASSESSMENT_FLOW_DESIGN.md`。

### 1. 什么是 Agent？

在这个项目里，Agent 是“角色 + 工具 + 状态 + trace + guardrail”的组合，例如 IntakeAgent 调 MaterialChecklistTool，RiskAgent 调 RiskRuleTool 和 RiskModelTool，PolicyAgent 调 PolicySearchTool。它不是简单聊天，而是接收结构化输入、执行确定任务、输出可被后续节点消费的结构化结果。

### 2. Agent 和普通 LLM 调用有什么区别？

普通 LLM 调用通常是一次 prompt 到一次 response。这个项目里的 Agent 有工作流状态、职责边界、工具调用记录、错误处理和结构化输出。LLM 只在 DecisionAgent 的报告生成阶段参与，而且不能改风险分数和最终审批状态。

### 2.1 项目里有哪些 tools？

当前有六类工具：`MaterialChecklistTool` 做材料校验，`RiskRuleTool` 做规则评分，`RiskModelTool` 调用 ML baseline，`PolicySearchTool` 做制度检索，`ComplianceGuardrailTool` 生成合规边界提示，`ReportGenerationTool` 生成报告并处理 LLM fallback。每次工具调用都会进入 `tool_calls` trace。

### 3. 为什么信贷审批适合多 Agent？

信贷审批天然由多个步骤组成：材料校验、风险评分、制度引用、合规检查和审批建议。拆成多 Agent 后，每个环节更容易测试、解释和审计，也方便替换模型或检索模块。

### 4. 为什么不使用单 Agent？

单 Agent 容易把制度检索、风险评分和报告生成混在一起，难以定位错误。多 Agent 可以把规则、ML、RAG、LLM 的职责分开，任何一个节点失败时也更容易 fallback。

### 5. Supervisor / Router / Handoff 是什么？本项目有没有用？

Supervisor/Router/Handoff 是多 Agent 系统里常见的调度模式，分别用于统一调度、动态路由和任务交接。本项目当前没有做复杂 supervisor，但 LangGraph 已经有材料缺失 conditional edge：材料不完整时跳过 RiskAgent，直接进入制度检索、合规检查和补件建议。

### 6. LangChain 和 LangGraph 区别是什么？

LangChain 更偏 LLM、retriever、tool、prompt 等组件集成；LangGraph 更适合有状态、多节点、可观测的工作流编排。本项目用 LangGraph 编排审批流程，用 LangChain 生态作为后续 LLM/RAG 组件扩展方向。

### 7. 本项目为什么用 LangGraph？

审批流程不是一次性问答，而是多个节点串联并共享状态。LangGraph 能清楚表达节点、状态和边；现在已经不是纯 pipeline，材料缺失时会走条件分支并跳过 RiskAgent，后续还能扩展高风险 senior review 分支。

### 8. Tool Calling 有什么风险？

风险包括调用未授权工具、参数被 prompt 注入污染、执行不可逆操作、把 LLM 输出直接当成业务决策。本项目的 tool calling 是后端工程侧显式工具调用，不让 LLM 直接调用审批写库工具，最终状态只能由 Java 人工审批接口写入。

### 8.1 为什么不让 LLM 直接审批？

信贷审批涉及合规、责任归属和风险控制。LLM 容易幻觉，也不能承担业务责任，所以它只能生成报告文本；`APPROVED`、`REJECTED`、`NEED_MORE_INFO` 必须由 Java 人工审批接口写入，并留下 approval record 和 audit log。

### 8.2 为什么演示页面可以一键生成申请，真实业务是不是也这样？

不是。页面里的按钮只是本地面试 Demo 快捷入口，用来快速创建一笔脱敏 mock 申请。真实业务里客户和贷款申请来自业务系统，AI Review 是审批人员在申请提交后触发的辅助审核，不负责生成真实客户数据。

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
