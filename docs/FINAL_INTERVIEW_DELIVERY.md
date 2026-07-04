# Final Interview Delivery

## 一句话介绍

SmartCreditMultiAgent 是一个基于 Spring Boot + FastAPI + LangGraph 的信贷审批辅助系统，把 Java 企业级后端、规则/ML 风控、制度 RAG、LLM 报告生成、多 Agent 编排、人工审批和审计留痕串成可演示闭环。

## 30 秒版本

我做的是一个金融科技场景的多 Agent 信贷审批辅助项目。Java 后端负责客户、贷款申请、AI report、Agent log、补件复审、人工审批和 audit log；Python 服务用 LangGraph 编排材料校验、风险评分、制度检索、合规检查、高风险 senior review 和报告生成。AI 只给审批建议，最终 approve/reject 必须由人工接口确认。

## 2 分钟版本

项目分为两个服务：`backend-service` 是 Spring Boot + MyBatis 的业务后端，承载登录、客户、贷款申请、状态机、AI review 触发、报告入库、日志查询、补件复审和人工审批；`agent-service` 是 FastAPI + LangGraph 的 AI 审批辅助服务，负责 IntakeAgent、RiskAgent、SeniorReviewAgent、PolicyAgent、ComplianceAgent 和 DecisionAgent。

RiskAgent 融合规则评分和 Logistic Regression baseline，PolicyAgent 使用本地 Markdown 制度库做 TF-IDF RAG，DecisionAgent 通过 LLM Provider 生成报告并保留 fallback。第 8 轮加入 tool system 和材料缺失分支，第 9 轮补齐 tool trace 端到端展示和高风险 SeniorReviewAgent，第 10 轮实现补件复审状态机。整个项目强调 human-in-the-loop、审计留痕和边界清晰，而不是让大模型自动放贷。

## 现场 Demo 顺序

1. 打开 `http://localhost:8080/demo.html`。
2. 点击“生成一笔脱敏演示申请”，创建 mock 客户和贷款申请并提交。
3. 在银行审批工作台触发 AI Review。
4. 查看 AI Review Summary、制度引用、Agent Logs 和 Tool Calls。
5. 点击 Need More Info，让申请进入补件流程。
6. 在“补件复审”卡片提交材料摘要，状态变为 `MATERIAL_UPDATED`。
7. 点击重新提交，状态变为 `RESUBMITTED`。
8. 再次触发 AI Review，状态回到 `AI_REVIEWED`，并新增 AI report。
9. 最后由人工 Approve 或 Reject。

## 必讲亮点

- Java 企业级后端：状态机、MyBatis、事务、审计日志、统一返回和异常处理。
- LangGraph 多 Agent：材料校验、风险评分、制度检索、合规检查、高风险复核、决策报告。
- Tool calling + tool trace：每个 Agent 的工具调用可在 Python response、Java log 和 Demo UI 中追踪。
- 风控规则 + ML baseline：规则为主，模型为辅助信号，模型失败时 fallback。
- 制度 RAG：本地模拟制度库检索，返回结构化 `policy_references`。
- LLM 报告生成 + fallback：Mock 默认稳定，真实 provider 仅本地显式启用。
- SeniorReviewAgent：高风险申请进入高级人工复核要求分支。
- 补件复审状态机：`NEED_MORE_INFO -> MATERIAL_UPDATED -> RESUBMITTED -> AI_REVIEWED`。
- 人工最终审批：AI 不写最终 approve/reject。
- 审计留痕：AI report、Agent log、approval record、material update record、audit log。

## 不能夸大的点

- 不是真实银行生产系统。
- 不接真实银行数据。
- 不自动放贷。
- 模型不是生产级风控模型。
- RAG 使用模拟制度库，不是真实银行制度库。
- Demo 补件只保存摘要，不上传真实身份证、手机号、征信报告或银行流水。

## 高频追问

### 真实业务中补件后怎么处理？

补件后不能直接沿用旧 AI 建议。项目里先从 `NEED_MORE_INFO` 进入 `MATERIAL_UPDATED`，再重提为 `RESUBMITTED`，之后必须重新 AI Review，最后才能人工终审。

### 重新 AI Review 会覆盖旧报告吗？

不会。每次 AI Review 都新增 `ai_decision_report`，旧报告保留，方便对比补件前后的 AI 建议。

### 为什么不让 LLM 自动审批？

信贷审批涉及合规和责任归属，LLM 只能辅助生成报告和解释依据。最终 `APPROVED` / `REJECTED` 必须由人工审批接口写入，并留下 approval record 和 audit log。

### 这个项目和普通 CRUD 的区别是什么？

核心不是表单增删改查，而是业务状态机、AI 辅助链路、Agent 编排、RAG/ML/LLM 集成、fallback、安全边界和审计追踪。

### 如果模型或 LLM 失败怎么办？

RiskAgent 会 fallback 到规则评分；DecisionAgent 会 fallback 到确定性报告。普通测试默认 Mock LLM，不依赖真实 API。
