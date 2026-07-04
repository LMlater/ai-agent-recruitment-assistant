# Demo Guide

## 第 12 轮推荐演示路径

最快静态检查：

```bash
python scripts/run_full_demo_stack.py --check-only
python scripts/check_demo_readiness.py --skip-services
```

如果当前机器没有 Docker，可以只做上面的静态检查，然后按源码模式启动；Docker unavailable 的具体处理见 `docs/TROUBLESHOOTING.md`。

Docker 模式：

```bash
docker compose up --build
```

源码模式：

```bash
docker compose up -d mysql redis
cd agent-service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

另开终端：

```bash
cd backend-service
mvn spring-boot:run
```

推荐现场顺序见 `docs/FINAL_DEMO_SCRIPT.md`。遇到端口、MySQL、Agent、Backend、Maven 或 Mock LLM 问题，优先查 `docs/TROUBLESHOOTING.md`。

## 第 11 轮：Docker Compose 一键演示栈

默认演示模式使用 Mock LLM，不需要真实 API Key，也不会读取或提交 `.env`。

先做静态检查：

```bash
python scripts/run_full_demo_stack.py --check-only
python scripts/check_demo_readiness.py --skip-services
```

启动完整演示栈：

```bash
docker compose up --build
```

启动后打开：

```text
Agent health: http://localhost:8001/health
Demo page: http://localhost:8080/demo.html
```

Compose 服务包括 `mysql`、`redis`、`agent-service`、`backend-service`。MySQL 初始化 SQL 仍挂载自 `backend-service/src/main/resources/db`，后端通过容器内地址访问 `mysql`、`redis` 和 `http://agent-service:8001`。

## 第 11 轮：Docker FAQ

- 构建较慢：首次构建会拉取 Python、Maven、JDK/JRE、MySQL、Redis 镜像，并安装 Python/Maven 依赖，属于正常现象。
- MySQL 首次启动等待：首次初始化数据库和执行 schema/data SQL 需要时间，`backend-service` 会等待 MySQL、Redis、Agent 健康后再启动。
- 端口冲突：本地需要空闲 `3306`、`6379`、`8001`、`8080`。如已被占用，先停止本机同端口服务或修改 compose 端口映射。
- 重置演示数据：执行 `docker compose down -v` 后再执行 `docker compose up --build`，会清空 Compose volume 中的 MySQL/Redis 数据。
- 安全边界：本地 demo 密码仅用于演示；生产环境不能复用默认密码，也不能把 `.env`、真实 API Key 或真实客户数据提交到仓库。

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

## 可视化 Demo 页面

启动两个服务后，浏览器打开：

```text
http://localhost:8080/demo.html
```

页面是原生 HTML + CSS + JavaScript，只用于本地面试演示，不是生产前端。新版页面分为两个 Tab：

1. 客户申请端：展示脱敏客户信息、贷款金额、期限、用途和提交状态。
2. 银行审批工作台：展示申请详情、AI Review、风险评分、制度引用、Agent 日志时间线、LLM 信息、人工审批和审批历史。

推荐点击顺序：

1. 在客户申请端点击“生成一笔脱敏演示申请”，自动执行 init admin、login、create customer、create loan application 和 submit application；admin 已存在时页面不会中断。该按钮只是本地面试 Demo 的 seed/mock fixture，真实业务中客户和贷款申请来自业务系统。
2. 切换到银行审批工作台，点击“触发 AI Review”。
3. 查看 AI Review Summary、风险评分、Policy References、Agent 日志时间线和 LLM Provider/Used/Error。
4. 如需展示接口结构，展开 Raw JSON 折叠面板，查看最近一次接口响应或完整 AI Report JSON。
5. 点击 Approve、Reject 或 Need More Info 中的一种人工审批。
6. 页面自动刷新审批历史并禁用三个人工审批按钮，避免重复审批。

AI Review 只展示辅助建议，最终 `APPROVED`、`REJECTED`、`NEED_MORE_INFO` 必须由人工审批按钮写入。

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
5. 打开 `http://localhost:8080/demo.html`，用页面完整点击 Java + Python 双服务 E2E 流程。
6. 也可以运行根目录 E2E demo 脚本，展示同一链路的命令行版本。
7. 最后打开 `docs/INTERVIEW_SCRIPT.md`，按常见 Q&A 准备追问。
