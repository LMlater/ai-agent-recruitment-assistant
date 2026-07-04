# Troubleshooting

本手册用于第 12 轮最终交付排查。它只覆盖本地 demo、CI、Docker Compose 和面试演示常见问题，不引入新的业务功能。

## 1. Docker 未安装

现象：

```text
docker: command not found
```

处理：

- 安装 Docker Desktop。
- 或改用源码模式启动。
- `python scripts/run_full_demo_stack.py --check-only` 会提示 Docker unavailable，并给出 source mode fallback。

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

## 2. 端口占用

需要确认以下端口空闲：

- `3306` MySQL
- `6379` Redis
- `8001` agent-service
- `8080` backend-service

处理方式：

```bash
docker compose down
```

如果本机已有同端口服务，先停止本机服务，或修改 `docker-compose.yml` 中的 ports 映射。

## 3. MySQL 初始化失败

说明：

- 第一次启动 MySQL 需要等待初始化。
- 初始化 SQL 来自 `backend-service/src/main/resources/db/schema.sql` 和同目录 seed 数据。
- 如果 volume 中已有旧数据，入口 SQL 不会重复执行。

重置方式：

```bash
docker compose down -v
docker compose up --build
```

## 4. Agent 服务不可达

先检查：

```text
http://localhost:8001/health
```

确认：

- `agent-service` 是否已经启动。
- Docker 模式下后端 `AGENT_SERVICE_BASE_URL` 应指向 `http://agent-service:8001`。
- 源码模式下后端 `AGENT_SERVICE_BASE_URL` 应指向 `http://localhost:8001`。
- 默认使用 Mock LLM，不需要真实 API Key。

## 5. Backend 启动失败

检查：

- MySQL 是否 ready。
- Redis 是否 ready。
- `MYSQL_URL`、`MYSQL_USER`、`MYSQL_PASSWORD` 是否匹配当前启动方式。
- `AGENT_SERVICE_BASE_URL` 是否匹配 Docker 模式或源码模式。
- Java 17 是否安装。

Docker 模式下后端会等待 MySQL、Redis、Agent healthcheck 通过后再启动。

## 6. GitHub Actions 没有运行或 badge 灰色

可能原因：

- GitHub Actions 未启用。
- workflow 刚提交尚未触发。
- 需要 push 到 `main` 或创建指向 `main` 的 pull request。
- 可进入 GitHub Actions 页面手动查看或重跑。
- 确认 workflow 文件在 `.github/workflows/ci.yml`。
- 确认 `workflow_dispatch` 已加入；Actions 页面应能手动 Run workflow。
- 如果 GitHub Actions 没有 workflow run，先确认仓库 Actions 是否启用，再 push 到 main 或手动 Run workflow。

CI badge 使用：

```markdown
[![CI](https://github.com/LMlater/ai-agent-recruitment-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/LMlater/ai-agent-recruitment-assistant/actions/workflows/ci.yml)
```

## 6.1 Docker Compose config 失败

现象：

```text
docker compose config
```

返回 Docker CLI 不存在、compose plugin 不存在，或 YAML/环境变量解析失败。

处理：

- 检查 Docker CLI 是否安装：`docker --version`。
- 检查 docker compose 版本：`docker compose version`。
- 确认当前目录是仓库根目录，且存在 `docker-compose.yml`。
- 如果当前机器没有 Docker，改用源码模式，并记录 Docker CLI unavailable。
- 有 Docker 的机器上先通过 `docker compose config`，再执行 `docker compose up --build`。

## 7. Windows 本地 Maven target AccessDenied

已知现象：

- Windows 本机可能在普通 `mvn test` 时复制 `target/classes/db/schema.sql` 出现 `AccessDeniedException`。
- GitHub Actions 使用 Linux runner 执行普通 `mvn test`。
- 本地临时 workaround 可以使用：

```bash
mvn -Dmaven.resources.skip=true test
```

这只是 Windows 本地临时方式，不是 CI 标准。不要把它写进 GitHub Actions。

## 8. Mock LLM 和真实 LLM 区分

说明：

- 默认 Mock LLM。
- 普通测试不调用真实 API。
- `.env` 不提交。
- 真实 provider 只允许本地显式启用。
- 不要把 DashScope/百炼/OpenAI Key 写入 README、文档、脚本、测试或提交历史。

## 9. Demo 页面操作失败

常见原因：

- 没有先生成演示申请。
- 没有触发 AI Review 就点击人工审批。
- `MATERIAL_UPDATED` 必须先 resubmit。
- `RESUBMITTED` 必须再次 AI Review 后才能 approve/reject。
- 最终 `APPROVED` / `REJECTED` 必须由人工审批接口写入，LLM/Agent 不写最终审批状态。

推荐顺序：

```text
生成演示申请 -> AI Review -> Need More Info -> 补件 -> 重新提交 -> 再次 AI Review -> 人工 Approve/Reject
```
