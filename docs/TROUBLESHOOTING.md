# Troubleshooting

## Round 15.1: 不知道上传哪个 CSV

如果不知道上传哪个 CSV，请使用仓库内置样例：

```text
docs/sample_import/loan_applications_sample.csv
```

注意：浏览器出于安全限制，不能自动读取或自动选择本地文件，所以需要用户手动点击“选择文件”，从本地仓库目录中选择该 CSV 上传。项目没有自动导入内置样例的专用按钮或接口。

## 第 15 轮：批量导入常见问题

### CSV 上传后部分行失败

这是预期行为。批量导入采用逐行容错：表头合法时，合法行会继续创建客户和贷款申请，非法行会进入 `errors` 列表，不会阻断整份文件。常见原因包括：

- 身份证号没有脱敏，出现完整 18 位身份证号或 17 位 + X。
- 手机号没有脱敏，出现完整 11 位手机号。
- 金额、年龄、月收入、负债、期限等数字字段为空或格式错误。
- CSV 列数不是 12 列，或表头和模板不一致。

### 上传 `.xlsx` 被拒绝

当前版本优先支持 CSV 导入，Excel 模板作为后续增强。处理方式：

1. 下载页面里的 CSV 模板，或使用 `docs/sample_import/loan_applications_sample.csv`。
2. 如已在 Excel 中维护数据，先“另存为 CSV UTF-8”。
3. 确认字段顺序保持为：

```text
applicant_name,id_card_masked,phone_masked,age,monthly_income,work_years,existing_debt,overdue_count,asset_proof_count,loan_amount,term_months,purpose
```

### 导入后看不到申请

先确认页面已登录 demo admin，再点击“刷新待审列表”。待审列表调用：

```text
GET /api/loan-applications?page=1&size=20
```

导入成功的申请会自动提交为 `SUBMITTED`，在页面显示为“待 AI 预审”。选择申请后可进入银行审批工作台触发 `AI预审`。

本手册用于第 12 轮最终交付排查。它只覆盖本地 demo、CI、Docker Compose 和面试演示常见问题，不引入新的业务功能。

## 1. Docker 未安装

现象：

```text
docker: command not found
```

处理：

- Docker 不是必须项，只是工程化交付加分项；有 Docker 的机器可选安装 Docker Desktop。
- 没有 Docker 时，改用“无 Docker 本地源码启动方式”。
- `python scripts/run_full_demo_stack.py --check-only` 会提示 Docker unavailable，并给出 source mode fallback。

## 1.1 无 Docker 本地源码启动方式

前置依赖：

- MySQL 8
- Redis
- Java 17
- Maven
- Python 3.11

创建数据库和本地 demo 用户：

```sql
CREATE DATABASE IF NOT EXISTS smart_credit_multi_agent DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'smartcredit'@'localhost' IDENTIFIED BY 'smartcredit_dev_password';
GRANT ALL PRIVILEGES ON smart_credit_multi_agent.* TO 'smartcredit'@'localhost';
FLUSH PRIVILEGES;
```

导入表结构：

```bash
mysql -usmartcredit -psmartcredit_dev_password smart_credit_multi_agent < backend-service/src/main/resources/db/schema.sql
```

确认本地 Redis 已启动后，启动 agent-service：

```bash
cd agent-service
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

另开终端启动 backend-service：

```bash
cd backend-service
mvn spring-boot:run
```

访问：

```text
http://localhost:8080/demo.html
```

如果本地 MySQL 用户、密码或端口不同，不要改仓库配置文件；用环境变量覆盖：

```bash
MYSQL_URL=jdbc:mysql://localhost:3306/smart_credit_multi_agent?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
MYSQL_USER=smartcredit
MYSQL_PASSWORD=smartcredit_dev_password
REDIS_HOST=localhost
REDIS_PORT=6379
AGENT_SERVICE_BASE_URL=http://localhost:8001
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
- 如果当前机器没有 Docker，改用无 Docker 本地源码启动方式，并记录 Docker CLI unavailable。
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

## 8.1 AI Review 长时间等待

现象：

- Demo 页面点击 AI Review 后等待 30-90 秒。
- 按钮处于禁用状态，并显示 `已等待 Ns`。

处理：

- 这不一定是卡死，可能是 `ReportGenerationTool` 正在调用真实 LLM 生成报告。
- 查看 `agent-service` 控制台，确认 DashScope/OpenAI-compatible provider 是否正在响应。
- 检查本地 provider 配置是否正确，但不要把真实 API Key 写入仓库。
- 如果现场网络不稳定或真实 LLM 超时，可以临时切回 Mock LLM fallback；普通测试和 CI 仍应保持 Mock。
- Redis 当前不是主链路强依赖；本地无 Redis 时，backend-service 仍可启动并完成核心 demo 链路。

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
