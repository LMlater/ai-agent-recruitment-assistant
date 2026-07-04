# Conversation Recovery

## 第 10 轮恢复要点

1. 第 8 轮成果：显式 Tool System、`tool_calls`、材料缺失跳过 RiskAgent、Java 人工审批状态机收紧。
2. 第 9 轮成果：Python tool trace -> Java log summary -> Demo UI 端到端展示，以及高风险 `SeniorReviewAgent` 条件分支。
3. 第 10 轮成果：补件复审轻量闭环，状态为 `NEED_MORE_INFO -> MATERIAL_UPDATED -> RESUBMITTED -> AI_REVIEWED`。
4. 新增 Java 表/实体/Mapper：`material_update_record`、`MaterialUpdateRecord`、`MaterialUpdateRecordMapper`，补件只保存 mock 摘要。
5. 新增接口：`POST /api/loan-applications/{id}/materials`、`POST /api/loan-applications/{id}/resubmit`、`GET /api/loan-applications/{id}/material-updates`。
6. 当前完整业务链路：创建申请 -> 提交 -> AI Review -> 人工 Need More Info -> 补件 -> 重新提交 -> 再次 AI Review -> 人工 Approve/Reject。
7. 每次 AI Review 都新增 AI report，不覆盖旧报告；补件、重提、AI Review、人工审批都通过 audit/record 留痕。
8. 下一轮建议：补 GitHub Actions CI 或 Docker Compose 一键启动，进一步提升工程交付完整度。

## 第 9 轮恢复要点

1. 本轮主题是 Tool Trace End-to-End + High Risk Senior Review Branch + Reassessment Flow Design。
2. Java `AgentReviewService` 仍不改 DB schema；`agent_execution_log.output_summary` 现在同时保留 `decision_report_generation` 与短格式 `tools=ToolName:STATUS(ms,error=...)`。
3. Demo 页面的 Agent Logs 时间线优先读取最新 AI Review 响应里的 `agent_results[].result.tool_calls`，用结构化卡片展示工具名、状态、耗时、输入/输出摘要和失败错误。
4. Python workflow 当前路径为：材料缺失 `intake -> policy -> compliance -> decision`；正常风险 `intake -> risk -> policy -> compliance -> decision`；高风险 `intake -> risk -> senior_review -> policy -> compliance -> decision`。
5. `SeniorReviewAgent` 只输出 `senior_review_required` 和 `senior_review_reasons`，不修改风险分数、不写最终审批状态、不调用任何 approve/reject/need-more-info 工具。
6. ComplianceAgent 和 DecisionAgent 会把 senior manual review 要求纳入合规提示和决策理由；高风险的 `final_decision=REJECT` 仍是 AI 辅助建议，不是数据库最终拒绝状态。
7. `docs/REASSESSMENT_FLOW_DESIGN.md` 记录真实业务补件后重提/重评方案：补件必须重新 AI review，旧 AI 报告不覆盖，所有材料更新和重提进入 audit log，最终审批仍由人工接口完成。
8. 普通测试继续使用 Mock LLM；不得提交 `.env`、真实 API Key、真实银行数据或敏感客户信息。

## 第 7 轮上下文保存约定

1. 从 2026-07-04 起，用户明确要求：后续项目中最重要的记忆、技术取舍、阶段进展、面试包装思路和下一步计划，都应及时整合进项目文档，防止 ChatGPT/Codex 对话丢失后无法恢复。
2. 长期稳定信息优先写入 `PROJECT_CONTEXT.md`；每轮恢复要点、验证记录和下一步建议优先写入 `docs/CONVERSATION_RECOVERY.md`；功能迭代写入 `docs/ITERATION_LOG.md`；简历和面试表达写入 `docs/RESUME_NOTES.md`。
3. 后续每轮结束时，尽量记录：本轮为什么做、做了什么、当前能跑到哪里、哪些仍是 mock、哪些安全边界不能突破、下一轮建议做什么。
4. 项目核心定位保持不变：这是面向求职和面试展示的金融科技工程项目，核心价值是 Java 后端工程 + 信贷审批业务流程 + LangGraph 多 Agent + 风控评分 + 制度 RAG + LLM 报告生成 + 人工复核与审计留痕。
5. AI/ML/RAG/LLM 只生成审批辅助建议，最终 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 必须由人工审批接口确认，不允许宣传为自动贷款审批系统。
6. 不得把真实 API Key、真实数据库密码、真实身份证、真实手机号、真实银行客户数据或其他敏感信息写入仓库。

## 第 8 轮恢复要点

1. 用户提出的三个关键考虑：Agent 不能只是线性 Python 类调用；LangGraph 需要体现条件分支；Java 人工审批不能从任意状态直接 approve/reject。
2. 本轮新增 `agent-service/app/tools/` tool system：`MaterialChecklistTool`、`RiskRuleTool`、`RiskModelTool`、`PolicySearchTool`、`ComplianceGuardrailTool`、`ReportGenerationTool`。
3. 每个执行过的 Agent 都在 `AgentResult.result.tool_calls` 中暴露工具调用 trace；Java DTO 的 `Map<String,Object>` 可兼容新增字段。
4. LangGraph `ReviewWorkflow` 已加入 `route_after_intake` conditional edge：材料缺失时跳过 RiskAgent，设置 `risk_skipped=true`、`risk_score=0`、`risk_level=HIGH`、`suggested_amount=0`，然后继续 policy/compliance/decision。
5. Java `ApprovalService` 状态机已收紧：approve/reject 只允许 `AI_REVIEWED`；need-more-info 只允许 `SUBMITTED` 或 `AI_REVIEWED`；`DRAFT` 和终态不允许人工审批。
6. Demo 页面已区分真实业务流程和本地面试演示快捷入口：按钮改为“生成一笔脱敏演示申请”，并说明演示按钮只是 seed/mock fixture，真实客户和申请来自业务系统。
7. 普通测试继续强制 Mock LLM，不调用真实 DashScope/百炼；不得提交 `agent-service/.env` 或任何真实密钥。
8. 下一步建议：可增加高风险 senior review 条件分支、审批退回后重新提交状态流、工具调用明细在 Java 日志表中的结构化存储。

## 可视化 Demo 页面恢复记录

1. 新增本地面试演示页：`backend-service/src/main/resources/static/demo.html`，访问地址为 `http://localhost:8080/demo.html`。
2. 页面使用原生 HTML + CSS + JavaScript，没有引入 Vue、React、npm 或前端构建工具。
3. 页面已从调试式按钮面板优化为“客户申请端”和“银行审批工作台”两个 Tab：客户申请端准备脱敏客户和已提交申请，银行审批工作台展示 AI Review、风险评分、制度引用、Agent 日志时间线、LLM 信息、人工审批和审批历史。
4. 新增“一键准备演示数据”按钮，自动执行 init admin、login、create customer、create loan application 和 submit application；admin 已存在时不会中断。
5. Raw JSON Panel 默认折叠，支持查看最近一次接口响应、完整 AI Report JSON 和复制 JSON；`reportJson` 为字符串时前端会尝试解析格式化。
6. 最新手动验证已跑通完整闭环：服务状态检查、登录、创建客户、创建申请、提交、AI Review、AI Report、Agent Logs、人工 Approve 和审批历史查询。
7. 验证结果：AI Summary 展示 `risk_level=LOW`、`risk_score=100`、`ai_report_id=8`；Policy References 展示 `R-004`、`M-003`、`P-002`、`P-003`、`P-004`；5 个 Agent 均为 `SUCCESS`，DecisionAgent 使用 `mock` LLM，`llm_error=null`。
8. 人工 Approve 后审批历史显示 `AI_REVIEWED -> APPROVED`，comment 为 `visual demo manual decision: approve`；AI 仍只提供辅助建议，最终状态由人工审批接口确认。
9. 页面只用于本地演示，没有修改数据库表结构，没有修改 AI review 主业务逻辑，也没有让 AI 自动审批最终状态；未记录 MySQL 密码或 API Key。
10. 文档入口已更新到 README、`docs/DEMO_GUIDE.md`、`docs/API_WALKTHROUGH.md` 和 `docs/INTERVIEW_SCRIPT.md`。

## 真实双服务 E2E 联调验证记录

1. 2026-07-03 本地真实双服务联调已通过：`agent-service` 运行在 `http://localhost:8001`，`backend-service` 运行在 `http://localhost:8080`。
2. `python scripts/check_demo_readiness.py` 返回 `ok=true`，backend 和 agent 均 `reachable=true`，`env_file_tracked=false`，`prints_api_key=false`。
3. `python scripts/run_e2e_credit_review_demo.py` 成功，`application_id=5`，`workflow_id=36a3af22-51b3-443c-8713-3e6ba9657586`，`risk_level=LOW`，`risk_score=100`，`ai_report_id=3`，`agent_log_count=5`，`decision_agent_llm_provider=mock`。
4. `python scripts/run_e2e_credit_review_demo.py --application-id 5 --manual-decision approve` 成功，`manual_decision_status=APPROVED`，最终审批由人工审批接口完成。
5. 本次联调使用 mock LLM，没有调用真实百炼；不得在文档或提交中记录 MySQL 密码、API Key、`.env` 或本地配置文件。

## 第 6 轮最新恢复要点

1. 面试交付版入口已经整理到 `README.md` 的“快速演示入口”，核心文档包括 `docs/DEMO_GUIDE.md`、`docs/ARCHITECTURE.md`、`docs/API_WALKTHROUGH.md`、`docs/INTERVIEW_SCRIPT.md`、`docs/RESUME_NOTES.md` 和 `docs/VALIDATION_LOG.md`。
2. readiness 检查脚本为 `scripts/check_demo_readiness.py`，只使用 Python 标准库，不读取或打印真实 API Key。
3. readiness 默认检查关键文件、后端 `http://localhost:8080` 和 Agent `http://localhost:8001` 服务可达性，以及 `.env` 是否被 git 跟踪。
4. 服务未启动时 readiness 会输出 JSON，`services.*.reachable=false`，不抛 Python stack trace，不伪造联调成功。
5. 面试讲解要强调：本项目是公开数据 + 模拟制度 + 工程验证，不是真实银行生产风控系统；AI 只给建议，人工接口最终确认。
6. 下一步建议：如需现场演示，先运行 `python scripts/check_demo_readiness.py`，再按 `docs/DEMO_GUIDE.md` 启动 agent-service 和 backend-service。

## 第 5 轮最新恢复要点

1. 项目级端到端演示入口为 `scripts/run_e2e_credit_review_demo.py`，默认通过 `BACKEND_BASE_URL=http://localhost:8080` 调用 Java 后端，再由后端调用 Python `agent-service`。
2. 脚本支持 `--application-id` 复用已有 `SUBMITTED` 或 `AI_REVIEWED` 申请；不传时会创建 mock customer、mock loan application 并提交。
3. 脚本默认只触发 AI review、查询 AI report 和 Agent logs；如果需要最终人工审批演示，可显式传 `--manual-decision approve|reject|need-more-info`。
4. Java DTO 能接收结构化 `policy_references`，`AgentResult.result` 能保留 `decision_report_generation` 嵌套对象。
5. Java 不改表结构，DecisionAgent 的 `llm_used`、`llm_provider`、`llm_error` 通过现有 `agent_execution_log.output_summary` 摘要展示。
6. 普通 Python 测试继续强制 Mock LLM，不调用真实百炼；真实 API key 只允许留在本地 `.env` 或系统环境变量中，不能提交。

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
14. 第 1.5 轮重点：修复 AI review 和普通状态更新的状态边界，补齐 AI 报告/Agent 日志查询接口，完善 seed 数据、测试和本地演示文档。
15. 对外检查建议：让下一位检查者优先看 README 的本地演示流程、`docs/ITERATION_LOG.md` 的第 1.5 轮记录，以及 Java/Python 测试覆盖。
16. 第 2 轮第一段重点：引入 UCI German Credit 公开数据集，完成下载、清洗映射、Logistic Regression baseline、模型评估、模型 artifact、RiskModelService 和模拟 seed SQL。
17. 第 2 轮第一段边界：当时模型只作为 artifact 和服务类存在；没有接入真实 LLM；没有接入 Chroma/FAISS；没有修改 LangGraph 工作流。
18. 第 2 轮第二段重点：RiskAgent 已接入 ML baseline，采用规则评分 + 模型概率融合，模型不可用时 fallback 到规则评分。
19. 当前仍未接入真实 LLM、RAG 向量库，也未修改 Java 数据库表；模型和 AI 都只作为审批辅助信号。
20. 第 3 轮第一段已加入本地制度 RAG 检索：模拟制度 Markdown 被切分为条款 chunk，TF-IDF + cosine similarity 返回结构化 `PolicyReference`，`/api/v1/reviews` 包含结构化 `policy_references`。
21. RAG 评估文件是 `data/eval/rag_questions.jsonl` 和 `data/eval/rag_eval_results.json`；运行 `cd agent-service && python scripts/evaluate_policy_retrieval.py` 可刷新指标。
22. 仍无真实 LLM、外部 Embedding API、Chroma/FAISS、真实银行制度、敏感数据、Java 数据库表结构修改或自动审批。
23. 第 3.1 轮修复 Java 后端 DTO 兼容：新增 `backend-service/src/main/java/com/smartcredit/agent/dto/PolicyReference.java`，`ReviewReport.policyReferences` 改为结构化引用列表，并新增 Jackson 反序列化测试。
24. RAG 评估结果 metadata 已改为相对路径；`rag_questions.jsonl` 和 `rag_eval_results.json` case 均保留 `expected_documents`。
25. 第 4 轮第一段新增 LLM Provider 抽象：`agent-service/app/services/llm/` 下包含 `LLMClient`、`MockLLMClient`、OpenAI-compatible 客户端、factory 和 prompt 模板。
26. `DecisionAgent` 现在先保留确定性规则结果，再用 `ReportGenerationService` 尝试生成自然语言审批辅助报告；LLM 失败时 fallback，不改变最终审批状态或风险分数。
27. 百炼接入仅通过环境变量启用，默认 `LLM_PROVIDER=mock`、`LLM_ENABLE_REAL_API=false`；真实 smoke test 默认 skip，仓库不得提交真实 API Key。
28. 第 4 轮第二段新增 pytest LLM 测试隔离：普通 `python -m pytest tests -q` 强制 Mock，不读取或调用真实百炼；直接运行 `tests/test_dashscope_live_smoke.py` 才允许加载本地 `.env` 做真实 smoke。
29. 新增 `agent-service/scripts/run_llm_review_demo.py`，用于输出端到端 review demo 的 workflow id、风险结果、制度编号和 `decision_report_generation`，不输出 API Key。
30. 第 4 轮第三段稳定真实 LLM demo：`run_llm_review_demo.py` 支持 `--mock`、`--real`、`--compact`，真实 demo 默认使用更长 timeout 和更小 max tokens，且 prompt 会压缩制度引用和风险字段。

不要写入真实密钥、真实身份证、真实手机号或其他敏感信息。
