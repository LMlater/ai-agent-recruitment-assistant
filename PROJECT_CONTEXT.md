# PROJECT_CONTEXT

## 用户背景

用户是华南理工大学数学本科、电气自动化方向研 0 学生，本科阶段做过 Java 全栈实习。

## 求职目标

目标是利用学历优势和项目经历，争取互联网中厂 Java 实习、银行科技岗、央国企科技岗，同时保留电网方向作为备选。

## 项目定位

SmartCreditMultiAgent 不是普通 CRUD，也不是简单 AI 聊天机器人，而是面向金融科技场景的多 Agent 智能信贷审批辅助系统。项目强调 Java 后端工程能力、金融业务流程理解、AI 工程集成能力、人工复核和审计留痕意识。

## 技术主线

- Spring Boot 负责信贷业务系统：登录、权限预留、客户、贷款申请、AI 报告、Agent 日志、人工审批、审计日志。
- Python FastAPI + LangGraph 负责多 Agent 编排、Mock RAG 和后续风控模型推理扩展。
- LangChain 只作为后续 LLM、Embedding、Retriever、向量库和结构化输出组件预留。

## 当前阶段

第一轮：双服务骨架、Mock 多 Agent 工作流、客户和贷款申请、AI 审批报告、Agent 执行日志、人工审批、项目文档。

## 后续迭代

- 第二轮：接入公开信贷数据和风控模型。
- 第三轮：接入 RAG 和向量库。
- 第四轮：接入真实 LLM，生成带制度引用的审批报告。
- 第五轮：补测试、Docker、README、评估报告、简历包装。
