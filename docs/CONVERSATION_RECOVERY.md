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
