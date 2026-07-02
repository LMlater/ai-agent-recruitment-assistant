# Demo Guide

## 项目一句话介绍

这是一个基于 Spring Boot + FastAPI + LangGraph 的多 Agent 智能信贷审批辅助系统。Java 后端负责客户、贷款申请、审批流程、AI 报告入库、Agent 日志和人工审批；Python Agent 服务负责材料校验、风险评分、制度 RAG 检索、合规检查和 LLM 报告生成。AI/ML/RAG/LLM 只提供辅助建议，最终审批必须由人工接口确认。

## 本地演示顺序

先跑普通测试，确认演示前状态干净：

```bash
cd agent-service
python -m pytest tests -q
python scripts/run_llm_review_demo.py --mock
```

```bash
cd backend-service
mvn test
```

启动 Python Agent 服务：

```bash
cd agent-service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

启动 Java 后端：

```bash
cd backend-service
mvn spring-boot:run
```

从仓库根目录运行端到端 demo：

```bash
python scripts/run_e2e_credit_review_demo.py
python scripts/run_e2e_credit_review_demo.py --application-id 1
python scripts/run_e2e_credit_review_demo.py --application-id 1 --manual-decision approve
```

演示前可以先跑 readiness 检查：

```bash
python scripts/check_demo_readiness.py
```

如果服务未启动，readiness 会输出 `reachable=false`，这是正常提示，不代表项目代码崩溃。

## E2E 输出字段解释

- `application_id`：本次演示使用的贷款申请 ID。
- `workflow_id`：Python Agent 工作流 ID，用于关联 Agent 执行日志。
- `final_decision_from_ai`：AI 给出的审批辅助建议，不是数据库最终审批结果。
- `risk_level`：融合规则评分和 ML baseline 后的风险等级。
- `risk_score`：风险评分，越高表示风险越低或审批倾向越积极，具体解释以项目规则为准。
- `suggested_amount`：AI 辅助建议金额。
- `ai_report_id`：Java 后端保存的 AI 报告 ID。
- `agent_log_count`：Java 后端查询到的 Agent 执行日志数量。
- `decision_agent_llm_provider`：报告生成来自 `mock` 或 `dashscope`。
- `policy_codes`：RAG 检索到的制度条款编号。
- `manual_approval_required`：始终为 `true`，表示最终状态必须由人工审批接口确认。

## 常见问题

- 后端没启动时，E2E 脚本会返回连接错误 JSON，不会打印 Python stack trace。
- agent-service 没启动时，后端触发 AI review 会失败，需要先启动 FastAPI 服务。
- `--mock` 不会调用真实百炼，适合稳定面试演示。
- 真实百炼超时会触发 fallback，这是保护机制，不是系统崩溃。
- 不要提交 `agent-service/.env`、`.env` 或任何真实 API Key。
- demo admin 账号只用于本地演示，生产环境不能使用默认账号密码。

## 面试讲解顺序建议

1. 先用一句话说明系统定位：信贷审批辅助，不是自动审批。
2. 展示 `docs/ARCHITECTURE.md` 的 Mermaid 图，说明 Java/Python 双服务边界。
3. 运行 `python scripts/check_demo_readiness.py`，展示文件、服务和安全检查。
4. 运行 `agent-service` 的 Mock demo，展示单服务 Agent + ML + RAG + LLM fallback 链路。
5. 运行根目录 E2E demo，展示 Java 调 Python、AI report 入库、Agent logs 查询和人工审批边界。
6. 最后打开 `docs/INTERVIEW_SCRIPT.md`，按常见 Q&A 准备追问。
