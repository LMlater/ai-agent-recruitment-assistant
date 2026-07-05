# Conversation Recovery

## Round 16.1 恢复要点

1. 本轮只修复正式前端 `frontend-service/src/App.vue` 的 Agent Trace / Tool Calls 展示字段兼容问题，不新增业务功能。
2. 根因不是后端 Agent 没执行，而是前端直接读取原始 `agentResults`，没有统一兼容后端与 Python Agent 返回的 `snake_case` 字段。
3. 新增 `normalizeAgentResult` / `normalizeToolCall` 等归一化函数，兼容 `agent_name`、`tool_name`、`duration_ms`、`input_summary`、`output_summary`、`error_message`。
4. `agentTimeline`、`toolCalls`、`hasSeniorReview` 都已改为基于 normalized agent results；高风险返回 `agent_name=SeniorReviewAgent` 时可以正确识别。
5. Agent Trace 会展示 Agent 名称、状态、耗时、输入摘要、输出摘要；无输出摘要时显示“该 Agent 暂无输出摘要，但状态已记录。”
6. Tool Calls 会展示真实工具名、中文说明、状态、耗时、输入摘要、输出摘要和错误信息；不再把真实工具统一显示成“Agent 工具调用”。

## Round 16 恢复要点

1. 本轮新增正式前端 `frontend-service`，技术栈为 Vue 3 + Vite + Element Plus；旧 `demo.html` 保留为 fallback。
2. `demo.html` 的待审列表 `AI预审` 按钮已接入 `{ aiReview: true }`，会显示 AI Review loading、禁用按钮、等待秒数和真实 LLM 30-90 秒提示。
3. `frontend-service` 的批量 AI 检测不新增后端批量接口，而是在前端顺序调用已有单笔 AI Review 接口，避免真实 LLM 并发限流。
4. 正式工作台主流程：登录 -> 手动上传 `docs/sample_import/loan_applications_sample.csv` -> 批量 AI 检测上传文件 -> 查看逐行结果 -> 打开详情查看 Agent Trace / Tool Calls / Policy References -> 人工审批。
5. 最终 `APPROVED / REJECTED / NEED_MORE_INFO` 仍必须由人工审批接口确认；AI/LLM 不拥有最终审批写库权限。
6. 当前本机没有 Node/npm，前端 build 需要在安装 Node 环境后运行；无 Node 时继续使用 `http://localhost:8080/demo.html` fallback。

## Round 15.1 恢复要点

1. 第 15.1 轮只做文案和静态测试小修，不新增业务接口。
2. 正确演示流程是：用户在 demo 页面手动选择 `docs/sample_import/loan_applications_sample.csv` 上传，后端解析上传文件后创建客户和贷款申请，并自动提交到 `SUBMITTED`。
3. 不存在自动导入内置样例的专用接口或按钮；不要把 CSV fixture 讲成系统绕过上传自动创建申请。
4. 浏览器不能自动读取或自动选择本地仓库文件，所以演示者必须手动点击“选择文件”。
5. 下载 CSV 模板只是辅助入口，用于下载同结构模板、编辑脱敏数据后再上传。

## 第 15 轮恢复要点

1. 本轮目标是让 Demo 更像真实信贷审批入口：支持客户经理/业务系统侧的脱敏 CSV 批量申请导入，并在银行审批工作台查看待审申请。
2. 后端新增 `LoanApplicationImportService`，导入字段为 `applicant_name,id_card_masked,phone_masked,age,monthly_income,work_years,existing_debt,overdue_count,asset_proof_count,loan_amount,term_months,purpose`。
3. 新增接口：`GET /api/loan-applications/batch-import-template` 下载 CSV 模板；`POST /api/loan-applications/batch-import` 上传 CSV 并返回成功/失败明细。
4. 批量导入会逐行创建 `Customer` 和 `LoanApplication`，并自动提交为 `SUBMITTED`；单行失败不阻断其他合法行，表头错误会直接失败。
5. 导入严格拒绝完整身份证号和完整手机号；不要把真实身份证、手机号、征信报告、银行流水或其他敏感信息写入仓库或上传到 demo。
6. `.xlsx` 当前不支持直接导入，提示用户先使用 CSV 模板；Excel 解析可作为后续增强，不属于本轮范围。
7. `demo.html` 仍是原生 HTML/CSS/JavaScript，没有引入 Vue/React；保留低/高风险快捷样例，同时新增批量导入、待审列表、中文状态映射和中文人工审批按钮。
8. 待审列表使用 `GET /api/loan-applications?page=1&size=20`；选中申请后同步页面状态并切换到银行审批工作台。
9. 本轮没有修改 Python Agent 主流程、没有改变人工最终审批边界、没有提交 `.env` 或真实 API Key。

## 第 14 轮恢复要点

1. 用户本机没有 Docker，但 MySQL 已初始化，backend-service 此前可启动。
2. Redis 当前不可用，但主链路不强依赖 Redis；无 Redis 时仍可先启动 backend-service 验证核心 demo。
3. agent-service `/health` 此前正常；用户希望继续使用真实 DashScope/OpenAI-compatible LLM，不强制切 Mock。
4. 本轮只优化 `backend-service/src/main/resources/static/demo.html` 的前端演示体验和必要文档，不改审批状态机、Java 后端业务逻辑或 Python Agent 主流程。
5. Demo UI 已加入能力 badge、演示步骤条、真实 LLM loading/elapsed seconds、终态解释、“重新开始演示”、Tool Calls 小卡片和 Agent Timeline 流程链。
6. 页面新增低风险/高风险样例按钮；高风险样例用于展示 HIGH risk 和 `SeniorReviewAgent`。
7. 真实 LLM 只用于报告生成，不拥有最终审批写库权限；最终 `APPROVED` / `REJECTED` 仍必须由人工按钮确认。
8. 普通测试和 CI 仍不依赖真实 LLM，不得提交 `.env`、真实 API Key、真实身份证、手机号、征信报告或银行流水。

## 无 Docker 启动文档修正

1. 本轮只修正文档，不新增业务功能，不修改代码逻辑、审批状态机、Agent 主流程或数据库业务表。
2. README 和 Troubleshooting 已明确：Docker 不是必须项，只是工程化交付加分项；有 Docker 的机器可选使用 Docker Compose。
3. 新增无 Docker 本地源码启动方式：本地安装 MySQL 8、Redis、Java 17、Maven、Python 3.11，创建 `smart_credit_multi_agent` 数据库和 `smartcredit` 用户，导入 `backend-service/src/main/resources/db/schema.sql`，再分别启动 `agent-service` 与 `backend-service`。
4. 无 Docker 模式访问入口仍是 `http://localhost:8080/demo.html`，默认 Mock LLM 和人工最终审批边界不变。

## 第 13 轮恢复要点

1. 第 13 轮是最终发布验收，不新增业务功能，不修改审批状态机、Agent 主流程或数据库业务表。
2. CI 增加 `workflow_dispatch`，GitHub Actions 页面可以手动 Run workflow；push 到 `main` 和面向 `main` 的 PR 仍会自动触发。
3. CI 增加 Docker Compose 静态校验，`delivery-package` job 在 Python/Java 测试通过后执行 `docker compose config` 和 readiness `--skip-services`。
4. 新增最终验收清单 `docs/FINAL_ACCEPTANCE_CHECKLIST.md`，覆盖功能、工程、安全边界、面试和当前已知限制。
5. 后续只建议：
   - 修 CI 实际失败；
   - 修 Docker 实测失败；
   - 根据简历投递反馈调整 README/简历表达；
   - 不再主动堆功能。
6. 继续保持默认 Mock LLM、不提交 `.env` 或真实 Key、不接真实银行数据、不让 AI/LLM/Agent 自动写最终审批状态。

## 第 12 轮恢复要点

1. 第 8 轮完成 Tool System、`tool_calls`、材料缺失条件分支和人工审批状态机收紧。
2. 第 9 轮完成 Tool Trace E2E、Java log summary、Demo UI 展示和 `SeniorReviewAgent` 高风险分支。
3. 第 10 轮完成补件复审状态机：`NEED_MORE_INFO -> MATERIAL_UPDATED -> RESUBMITTED -> AI_REVIEWED`，以及 `material_update_record`。
4. 第 11 轮完成 CI、Dockerfile、Docker Compose 四服务编排、readiness 检查和一键栈脚本。
5. 第 12 轮完成 README polish、`docs/TROUBLESHOOTING.md`、`docs/FINAL_DEMO_SCRIPT.md`、最终交付文档收口和 `run_full_demo_stack.py` 友好提示。
6. 当前项目已经进入最终面试交付版；后续不建议继续堆业务功能，只建议小修 bug、修 CI 失败、根据真实投递反馈调整 README/简历表达。
7. 必须继续保持：默认 Mock LLM、不提交 `.env` 或真实 Key、不接真实银行数据、不让 AI/LLM/Agent 自动写最终审批状态。

## 第 11 轮恢复要点

1. 第 11 轮主题是 CI + Docker Compose 一键交付 + 最终工程包装，不新增业务功能。
2. 已保留第 8 轮 Tool System/tool_calls、 第 9 轮 SeniorReviewAgent/tool trace、 第 10 轮补件复审状态机和 `material_update_record`。
3. 新增 `.github/workflows/ci.yml`：Agent Python 3.11 pytest、Backend Java 17 Maven test、readiness `--skip-services` 三个任务。
4. 新增 `agent-service/Dockerfile`、`backend-service/Dockerfile` 和各自 `.dockerignore`，默认 Mock LLM，不复制 `.env`。
5. `docker-compose.yml` 现在包含 `mysql`、`redis`、`agent-service`、`backend-service`，并带健康检查和容器内依赖地址。
6. 新增 `scripts/run_full_demo_stack.py`，标准库实现，`--check-only` 可检查 Docker、交付文件、Compose 服务和 readiness。
7. `scripts/check_demo_readiness.py` 已增强为检查 CI workflow、Dockerfile、Compose 四服务和最终交付文档；`--skip-services` 不要求本地服务启动。
8. 后续如果继续开发，优先保持 Mock LLM 默认、安全边界、人工最终审批和已有状态机，不要把本地 `.env` 或真实 Key 写入仓库。

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
## Round 17 恢复要点

1. 当前正式前端已经从单页工作台拆成 Vue Router 页面：`/login`、`/workspace`、`/applications/:applicationId`。
2. 继续演示时优先使用 `frontend-service`，`demo.html` 仅作为 fallback 保留。
3. Header 登录态由 `smartcredit.frontend.token` 判断；“退出登录”会清理 token、当前申请和 `smartcredit.frontend.lastBatchRows`。
4. 工作台刷新后恢复批量结果属于预期行为；若要验证未登录门控，先退出登录或清空 localStorage。
5. 左侧导航和顶部能力标签已经是真实快捷入口。没有当前申请时，详情/Trace/Policy/Approval 入口会提示“请先选择申请”。
6. 本轮没有改 Java 审批状态机、Python Agent 流程，也没有新增后端批量 AI Review 接口。
## Round 17.1 恢复要点

1. 本轮修复的是正式前端 `/applications/:id?tab=tools` 可能显示“暂无 Tool Calls”的问题。
2. 根因：详情页读取的是 Java 持久化后的 Agent logs，工具调用常以 `tools=MaterialChecklistTool:SUCCESS(0ms)` 形式保存在 `outputSummary` 中，而不是结构化 `result.tool_calls`。
3. `ApplicationDetail.vue` 现在优先使用结构化 tool calls；结构化为空时，从 `outputSummary` 的 `tools=...` 解析出 Tool Calls 卡片。
4. Agent Trace 已增加中文职责说明，同时保留英文原始摘要；Tool Calls 已增加工具中文说明、所属 Agent 和来源。
5. 本轮没有改后端业务逻辑、Agent 流程、审批状态机、数据库字段或批量 Review 接口。
