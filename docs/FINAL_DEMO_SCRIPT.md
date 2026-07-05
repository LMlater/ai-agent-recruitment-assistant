# Final Demo Script

## 第 15 轮演示提示：从批量导入进入审批工作台

- 面试时可以先说明：真实业务里客户和贷款申请通常来自业务系统、客户经理台账或批量导入，而不是由 AI Agent 自动生成。
- 在客户申请端使用“下载 CSV 模板”，或直接打开 `docs/sample_import/loan_applications_sample.csv` 说明字段。
- 上传脱敏 CSV 后，导入服务会创建客户和贷款申请，并把申请自动提交为 `SUBMITTED`，页面展示为“待 AI 预审”。
- 切到银行审批工作台，点击“刷新待审列表”，选择一笔申请，再触发 `AI预审`。
- 人工审批按钮使用中文表达：“人工通过”“人工拒绝”“要求补件”。要强调 AI/ML/RAG/LLM 只给审批辅助建议，最终状态仍由人工接口写入。
- 低/高风险按钮仍可作为快速演示样例，尤其高风险样例适合展示 `SeniorReviewAgent`；但它们只是本地面试快捷入口。

本脚本用于面试现场演示。原则是讲清楚工程能力和业务边界，不夸大为真实银行生产系统。

## 第 14 轮演示提示：真实 LLM 等待体验

- 面试现场可以使用真实 DashScope/OpenAI-compatible LLM 生成审批辅助报告，但要提前说明真实 LLM 报告生成可能需要 30-90 秒。
- 等待 AI Review 时，不要重复点击按钮；可以讲解页面上的 Agent trace、Tool Trace、Policy RAG、human-in-the-loop 边界和最终人工审批责任。
- 如果现场网络不稳定、真实 LLM 超时或 provider 不可用，可以临时切回 Mock LLM fallback；普通测试和 CI 仍不依赖真实 LLM。
- 推荐演示高风险样例，用来展示 `SeniorReviewAgent` 条件分支；低风险样例可能不会进入 `SeniorReviewAgent`，这是正常路径。
- 需要强调：真实 LLM 只用于报告生成，不拥有最终审批写库权限，最终 `APPROVED` / `REJECTED` 必须由人工按钮确认。

## 3 分钟演示脚本

第 1 分钟：介绍项目定位和架构。

- 这是 Spring Boot 后端 + FastAPI/LangGraph Agent 的信贷审批辅助项目。
- Java 负责登录、客户、贷款申请、状态机、AI report 入库、Agent logs、人工审批和 audit log。
- Python 负责材料检查、风险评分、制度检索、合规提示、SeniorReviewAgent 和报告生成。

第 2 分钟：演示 AI Review + Tool Calls + SeniorReviewAgent。

- 打开 `http://localhost:8080/demo.html`。
- 生成一笔脱敏演示申请。
- 触发 AI Review。
- 展示风险评分、policy references、Agent Logs、Tool Calls。
- 如果是高风险样例，说明 SeniorReviewAgent 只生成高级人工复核要求，不写最终审批状态。

第 3 分钟：演示 Need More Info -> 补件 -> 重提 -> 再次 AI Review -> 人工终审。

- 人工点击 Need More Info。
- 录入补件摘要，状态进入 `MATERIAL_UPDATED`。
- 点击重新提交，状态进入 `RESUBMITTED`。
- 再次触发 AI Review，状态回到 `AI_REVIEWED`。
- 人工 Approve 或 Reject，并展示审批历史和审计留痕。

## 5 分钟演示脚本

1. 打开 demo 页面：`http://localhost:8080/demo.html`。
2. 说明页面只用于本地面试 demo，不是生产前端。
3. 生成脱敏演示申请，强调它是 seed/mock fixture。
4. 触发 AI Review。
5. 解释 Agent 顺序：IntakeAgent、RiskAgent、SeniorReviewAgent、PolicyAgent、ComplianceAgent、DecisionAgent。
6. 展示 Tool Calls：工具名、状态、耗时、输入/输出摘要、错误信息。
7. 展示 Policy References：制度编号、制度片段和命中来源。
8. 展示 SeniorReviewAgent：高风险时进入高级人工复核要求分支。
9. 人工点击 Need More Info。
10. 提交补件摘要，说明不上传真实身份证、手机、征信报告或流水。
11. 重新提交申请。
12. 再次 AI Review，并说明新 AI report 不覆盖旧报告。
13. 人工 approve/reject。
14. 总结 audit log、approval record、material update record 和 human-in-the-loop 边界。

## 面试官追问路线

### 为什么拆 Java + Python？

Java 更适合承载企业业务后端、事务、权限、状态机和审计；Python 更适合 AI/ML/RAG/LangGraph 生态。两个服务通过 HTTP 解耦，方便独立测试和替换。

### Agent 和普通 LLM 调用区别？

普通 LLM 调用通常是一段 prompt 到一次 response。本项目的 Agent 有明确角色、工具、状态、trace、fallback 和结构化输出；LLM 只参与报告生成，不拥有最终审批权限。

### Tool calling 怎么体现？

每个 Agent 调用明确工具，例如材料检查、规则评分、模型信号、制度检索、合规护栏、报告生成。`tool_calls` 会在 Python response、Java log summary 和 Demo UI 中展示。

### 为什么要 RAG？

信贷审批建议需要制度依据。RAG 用本地模拟制度库返回结构化 policy references，让报告能解释“为什么这样建议”，而不是只给黑盒结论。

### 为什么要 ML baseline？

ML baseline 用公开 German Credit 数据训练，只作为风险辅助信号，和规则评分融合。它证明模型工程链路，但不是生产级风控模型。

### 为什么不自动审批？

信贷审批涉及合规、责任归属和审计。AI/ML/RAG/LLM 只生成辅助建议，最终 `APPROVED` / `REJECTED` 必须由人工审批接口写入。

### 高风险为什么要 SeniorReviewAgent？

高风险申请需要更严格的人工复核。SeniorReviewAgent 只输出 senior review required 和原因，不修改风险分数，不替代人工 senior reviewer。

### 补件后为什么要重新 AI Review？

补件改变了申请事实基础，不能沿用旧 AI report。项目用 `NEED_MORE_INFO -> MATERIAL_UPDATED -> RESUBMITTED -> AI_REVIEWED` 保证补件后必须重新评估，旧报告保留用于审计。

### Docker/CI 做了什么？

CI 分别跑 Python pytest、Java Maven test 和 readiness 静态检查。Dockerfile 和 Compose 支持 MySQL、Redis、Agent、Backend 四服务本地一键演示，默认 Mock LLM。

### 这个项目离真实银行生产还差什么？

还需要真实数据治理、模型验证与监控、权限体系、风控策略引擎、真实制度库和向量库、灰度发布、告警、合规模型评审、安全审计和生产级运维。本项目是公开数据 + 模拟制度 + 工程验证的面试展示版。
