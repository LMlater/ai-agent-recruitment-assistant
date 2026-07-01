# Conversation Recovery

## 重要上下文

1. 用户背景：华南理工大学数学本科，电气自动化方向研 0，本科阶段做过 Java 全栈实习。
2. 求职目标：互联网中厂 Java 实习、银行科技岗、央国企科技岗，同时保留电网方向作为备选。
3. 项目名称：SmartCreditMultiAgent。
4. 项目中文名：基于 Spring Boot + FastAPI + LangGraph 的多 Agent 智能信贷审批辅助系统。
5. 项目定位：不是普通 CRUD，也不是简单 AI 聊天机器人，而是金融科技场景下的多 Agent 信贷审批辅助系统。
6. 技术架构：Spring Boot backend-service + Python FastAPI agent-service。
7. Agent 服务使用 LangGraph 编排多 Agent 工作流，LangChain 只作为后续 LLM、Embedding、Retriever、RAG 组件集成。
8. 多 Agent 包括 IntakeAgent、RiskAgent、PolicyAgent、ComplianceAgent、DecisionAgent。
9. AI 只做审批辅助建议，最终审批必须由人工确认。
10. 数据方案：第一轮用模拟 seed 数据，后续使用公开信贷数据集和模拟制度文档，不使用真实银行客户数据。
11. 迭代计划：第一轮双服务骨架，第二轮数据和风控模型，第三轮 RAG，第四轮真实 LLM，第五轮工程化和简历化。
12. 学习计划：每天刷 LeetCode、复习 Java 八股、阅读项目代码、学习 Agent/RAG 面试知识。
13. 简历包装方向：Java 后端工程 + 金融业务流程 + LangGraph 多 Agent + RAG 制度检索 + 风控评分 + 审计留痕。

不要写入真实密钥、真实身份证、真实手机号或其他敏感信息。
