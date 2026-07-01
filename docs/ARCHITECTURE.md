# Architecture

## 双服务架构

SmartCreditMultiAgent 使用双服务架构：

- `backend-service`：Spring Boot 信贷业务系统，负责业务状态、持久化、审计和人工审批。
- `agent-service`：FastAPI + LangGraph 多 Agent 审批辅助服务，负责生成结构化 AI 审批建议。

## Java 后端职责

- 用户登录、JWT 和基础角色结构。
- 客户信息管理，只保存脱敏身份证和脱敏手机号。
- 贷款申请生命周期管理。
- 调用 Python Agent 服务。
- 保存 AI 审批报告、Agent 执行日志、人工审批记录和审计日志。
- 通过人工审批接口完成最终状态变更。

## Python Agent 服务职责

- 接收客户和贷款申请结构化信息。
- 使用 LangGraph 编排 `IntakeAgent -> RiskAgent -> PolicyAgent -> ComplianceAgent -> DecisionAgent`。
- 返回 `workflow_id`、风险等级、风险分、建议额度、摘要、Agent 执行结果和报告。

## 数据流

```text
Client -> backend-service -> MySQL
                       |
                       v
                 agent-service
                       |
                       v
        LangGraph multi-agent workflow
                       |
                       v
backend-service saves report/logs/audit and returns result
```

## 为什么用 LangGraph

LangGraph 适合表达有状态、多节点、可扩展条件分支的审批流程。第一轮使用固定顺序工作流，后续可在材料缺失、高风险、合规警告等节点加入 conditional edge。LangChain 只作为后续 LLM、Embedding、Retriever、向量库和结构化输出的组件集成层。
