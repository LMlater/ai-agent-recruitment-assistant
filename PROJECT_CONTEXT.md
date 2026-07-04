# PROJECT_CONTEXT

## 第 12 轮当前状态

- 当前项目已进入最终面试交付版：README 顶部有 CI badge、项目定位、最快启动、7 步 Demo 和不能夸大的边界。
- 新增 `docs/TROUBLESHOOTING.md` 和 `docs/FINAL_DEMO_SCRIPT.md`，用于现场排障和按时间演示。
- 后续优先小修 bug、修复 CI 失败、调整 README/简历表达，不建议继续堆业务功能。
- 第 8/9/10/11 轮成果保持不回退：Tool System、Tool Trace + SeniorReviewAgent、补件复审、CI/Docker Compose 都继续保留。

## 第 11 轮当前交付状态

- 第 11 轮已补齐 CI + Docker Compose + Dockerfile + readiness 一键交付包装：默认 Mock LLM，不依赖真实 API Key，不提交 `.env`。
- GitHub Actions 覆盖 Python Agent pytest、Java Maven test 和 `check_demo_readiness.py --skip-services`。
- Docker Compose 可启动 `mysql`、`redis`、`agent-service`、`backend-service` 四服务，演示入口为 `http://localhost:8080/demo.html`。
- 第 8/9/10 轮成果继续保留：Tool System/tool_calls、SeniorReviewAgent/tool trace、补件复审状态机和人工最终审批边界。

## 用户背景

用户是华南理工大学数学本科、电气自动化方向研 0 学生，本科阶段做过 Java 全栈实习。

## 求职目标

目标是利用学历优势和项目经历，争取互联网中厂 Java 实习、银行科技岗、央国企科技岗，同时保留电网方向作为备选。

## 项目定位

SmartCreditMultiAgent 不是普通 CRUD，也不是简单 AI 聊天机器人，而是面向金融科技场景的多 Agent 智能信贷审批辅助系统。项目强调 Java 后端工程能力、金融业务流程理解、AI 工程集成能力、人工复核和审计留痕意识。

这个项目的核心目的不是证明“会调用 LLM API”，而是证明：能够把 Java 企业级后端、信贷审批业务、风控评分、制度 RAG、LLM 报告生成、Agent 工作流、人工复核和审计留痕整合成一个可运行、可演示、可解释、可写入简历的金融科技工程项目。

## 上下文保存约定

从第 7 轮开始，后续对项目定位、技术取舍、重要实现进展、面试包装、风险边界和下一步计划的关键记忆，都应及时沉淀到项目文档中，避免未来 ChatGPT/Codex 对话丢失后无法恢复。

优先保存位置：

- `PROJECT_CONTEXT.md`：长期稳定的项目定位、用户背景、求职目标、技术主线和关键约定。
- `docs/CONVERSATION_RECOVERY.md`：每轮恢复上下文、最新进展、重要边界、验证记录和下一步建议。
- `docs/ITERATION_LOG.md`：按轮次记录功能迭代和工程变更。
- `docs/RESUME_NOTES.md`：沉淀可用于简历和面试讲解的项目亮点。

不要写入真实 API Key、真实数据库密码、真实身份证、真实手机号、真实银行客户数据或其他敏感信息。

## 技术主线

- Spring Boot 负责信贷业务系统：登录、权限预留、客户、贷款申请、AI 报告、Agent 日志、人工审批、审计日志。
- Python FastAPI + LangGraph 负责多 Agent 编排、风控模型辅助信号、制度检索和 LLM 报告生成扩展。
- LangChain 只作为后续 LLM、Embedding、Retriever、向量库和结构化输出组件预留。
- AI/ML/RAG/LLM 都只生成审批辅助建议，不允许自动完成最终贷款审批。

## 当前阶段

当前项目已从第一轮骨架演进到面试交付版：

- 已完成 Java backend-service + Python agent-service 双服务闭环。
- Agent 工作流使用 LangGraph 编排 IntakeAgent、RiskAgent、PolicyAgent、ComplianceAgent、DecisionAgent。
- RiskAgent 已融合规则评分与 Logistic Regression baseline，模型不可用时 fallback 到规则评分。
- PolicyAgent 已实现本地 Markdown 制度库的 TF-IDF RAG baseline，返回结构化制度引用。
- DecisionAgent 已支持 LLM Provider 抽象，可使用 Mock LLM 或通过环境变量启用 DashScope/OpenAI-compatible 客户端，真实调用失败时 fallback。
- Java 后端已能保存 AI report、Agent execution logs、approval record 和 audit log，并确保最终 APPROVED/REJECTED/NEED_MORE_INFO 必须由人工审批接口确认。
- 第 10 轮已实现补件复审轻量闭环：`NEED_MORE_INFO -> MATERIAL_UPDATED -> RESUBMITTED -> AI_REVIEWED`，补件摘要、重提、复评和人工终审均可审计追踪。
- 已有本地可视化 demo 页面、端到端演示脚本、readiness 检查脚本和面试讲解文档。

## 后续迭代

优先级从“继续堆功能”转为“增强面试可解释性、工程完整度和风险边界”。建议后续按以下方向推进：

1. 第 7 轮：完善项目恢复文档、迭代日志和面试讲解材料，保证换对话后可继续开发。
2. 第 8 轮：加强 LangGraph 条件分支，例如材料缺失直接 NEED_MORE_INFO，高风险进入更严格合规说明，但仍不自动最终审批。
3. 第 9 轮：补 Dockerfile、CI 或一键启动脚本，提升工程交付完整度。
4. 第 10 轮：准备简历版本、面试问答、项目难点和可演示脚本。
