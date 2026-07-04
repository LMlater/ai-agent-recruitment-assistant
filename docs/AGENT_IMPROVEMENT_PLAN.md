# Agent Improvement Plan

## 背景

第 8 轮开始前，用户提出三个关键考虑：

1. Agent 中是否应该体现 tool 调用，否则难以区分 Agent 和普通 LLM 调用。
2. 当前“一键生成所有数据，然后直接 AI Review”的演示方式偏 demo 化，不够像真实信贷流程。
3. 希望参考 GitHub 上高 star Agent 项目的设计，判断本项目还能改进什么、还能增加什么功能。

本文件用于沉淀第 8 轮之后的 Agent 改造方向，防止对话丢失。

## 对高星 Agent 项目的观察

代表项目/框架的共同设计方向：

- OpenAI Agents SDK：Agent 通常由 instructions、tools、guardrails、handoffs、human-in-the-loop、sessions 和 tracing 组成。
- Microsoft AutoGen / Agent Framework：强调多 Agent 应用、MCP/tool、multi-agent orchestration、human-in-the-loop、observability、workflow patterns 和生产级治理。
- CrewAI：区分自主协作的 Crews 与事件驱动、可控的 Flows，强调 role、goal、task、tool、memory、guardrail 与 workflow control。
- Pydantic AI：强调 type-safe agent、dependency injection、structured output、tools、human approval、evals、durable execution 和 graph support。

这些项目的共同启发：

1. Agent 不只是“一个类 + 一个 prompt”，而是“角色/目标 + 工具 + 状态 + 结构化输出 + 观测 + 安全边界”。
2. 金融场景不适合完全自主执行，应采用 workflow / flow / graph 风格的受控编排。
3. Tool calling 应优先从只读、可审计、可回放的业务工具开始，而不是让 LLM 直接调用写库或最终审批工具。
4. Human-in-the-loop 是金融信贷项目的核心卖点，不能被弱化。
5. 需要将 Agent 执行过程沉淀为 trace / log / eval，而不只是给出最终结论。

## 本项目的改造原则

### 1. 不把 LLM 直接变成审批员

即使引入 tool calling，也不允许 LLM/Agent 直接调用最终 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 写库接口。最终状态仍必须由 Java 后端的人工审批接口确认。

### 2. Tool 先做“领域能力封装”

第 8 轮建议新增 `agent-service/app/tools/`，把现有能力显式封装为工具：

- `MaterialChecklistTool`：检查年龄、收入、额度、期限、资产证明等材料完整性。
- `RiskRuleTool`：输出规则评分、扣分原因和债务收入比。
- `RiskModelTool`：调用 Logistic Regression baseline，输出模型概率、模型等级和解释。
- `PolicySearchTool`：调用本地制度 RAG，返回结构化制度引用。
- `ComplianceGuardrailTool`：输出 AI/ML/RAG/LLM 使用边界、人工复核和审计留痕要求。

这些工具由各 Agent 调用，并把 tool name、input summary、output summary、status、duration 记录到 Agent result 或 report 中。

### 3. 先做受控工具调用，不做危险通用工具

暂不引入浏览器、shell、文件写入、数据库写入等高风险工具。金融审批场景优先使用只读、确定性、可测试的工具。

### 4. 演示流程要区分“真实业务流程”和“演示快捷入口”

后续 demo 页面应明确区分：

- 真实业务流程：客户建档 -> 创建申请 -> 提交申请 -> 银行审批员触发 AI Review -> 查看 AI 报告/制度引用/Agent 日志 -> 人工最终审批。
- 演示快捷入口：一键准备演示数据，只是为了面试时快速生成一笔脱敏、已提交的 mock 申请，不代表真实业务中自动生成客户和贷款申请。

建议将按钮文案从“一键准备演示数据”优化为“生成一笔脱敏演示申请”，并在页面上注明“仅用于本地面试 demo”。

### 5. LangGraph 要从线性 pipeline 升级为条件审批图

第 8 轮建议实现：

```text
START
  -> intake
  -> route_after_intake
       missing_materials -> policy -> compliance -> decision
       complete          -> risk -> policy -> compliance -> decision
  -> END
```

第 8.5 或第 9 轮可以继续加入：

```text
risk == HIGH -> high_risk_compliance -> policy -> decision
risk != HIGH -> policy -> compliance -> decision
```

注意：即使 high risk 走特殊分支，也只是生成更严格的人工复核建议，不自动最终拒绝。

### 6. Java 审批状态机已收紧

Java 已限制 AI review 不能写最终状态、普通状态更新不能写最终状态；第 8 轮继续收紧了人工审批入口：

- `DRAFT` 不允许人工 approve/reject。
- `SUBMITTED` 应先 AI review 或要求补充材料，不能直接 approve/reject。
- `AI_REVIEWED` 可以 approve/reject/need-more-info。
- `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 不允许重复最终审批，除非后续显式设计“重新提交/复审”流程。

### 7. 后续可选增强

- Tool trace：在 AgentResult.result 中加入 `tool_calls` 数组。
- Agent eval：为低/中/高风险、材料缺失、高负债、高逾期等 case 建立固定评估集。
- Observability：在 demo 页面展示 tool trace，而不是只展示 Agent summary。
- CI：增加 GitHub Actions，自动跑 `agent-service` pytest、`backend-service` mvn test 和 readiness `--skip-services`。
- Docker：补 backend-service 和 agent-service Dockerfile，最终实现一条命令启动完整 demo。

## 第 8 轮建议任务拆分

优先顺序：

1. 新增 Python tool 层和 `tool_calls` 结构，让 Agent 明确体现工具调用。
2. LangGraph 增加材料缺失条件分支。
3. Java 人工审批状态机收紧。
4. Demo 页面文案调整：区分真实流程和一键演示数据。
5. 更新测试、架构文档、面试话术和恢复文档。

## 不做什么

- 不让 LLM 调用写库工具。
- 不接真实银行数据。
- 不把模型包装成生产级风控模型。
- 不默认调用真实 LLM API。
- 不提交 `.env`、真实 API Key、真实数据库密码、真实身份证、真实手机号或真实银行客户信息。

## 第 8 轮已完成

本轮把 Agent 工程从线性 demo 推进到更可解释的工具化工作流：

- Agent = role + tool + state + trace + guardrail。
- `agent-service/app/tools/` 承载具体能力，Agent 负责编排和状态更新。
- `AgentResult.result.tool_calls` 暴露工具调用记录，便于面试展示和 Java 后端兼容保存。
- LangGraph 在 Intake 后增加材料缺失条件分支，缺失材料时跳过 RiskAgent，避免无效输入进入风控计算。
- Java 人工审批状态机收紧，防止 `DRAFT`、`SUBMITTED` 直接 approve/reject，以及终态重复审批。

## 后续建议

1. 在 RiskAgent 后增加高风险 senior review 条件分支。
2. 为 `tool_calls` 增加 Java 侧结构化展示或单独日志字段。
3. 设计 `NEED_MORE_INFO -> 补件 -> SUBMITTED` 的复审状态流。
4. 将当前本地 TF-IDF RAG 替换为可插拔向量检索实现，但继续保留 mock/test 默认路径。
