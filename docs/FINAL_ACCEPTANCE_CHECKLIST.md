# Final Acceptance Checklist

本清单用于第 13 轮发布前验收。它只检查当前面试交付包是否完整，不新增业务功能，也不替代 GitHub Actions 页面和本地 Docker 实测结果。

## 1. 功能验收

- [ ] 客户/贷款申请创建：demo 页面可生成脱敏演示客户和贷款申请。
- [ ] 提交申请：贷款申请可从草稿进入已提交状态。
- [ ] AI Review：银行审批工作台可触发 AI 审批辅助评估。
- [ ] Agent logs：Java 后端可查询并展示 Agent 执行日志。
- [ ] Tool calls：Demo UI 可展示工具名、状态、耗时、输入摘要和输出摘要。
- [ ] Policy references：AI report 中保留结构化制度引用。
- [ ] SeniorReviewAgent 高风险分支：高风险申请进入高级人工复核要求分支。
- [ ] Need More Info：人工可要求补充材料。
- [ ] 补件：补件只保存 mock 摘要，不上传真实敏感材料。
- [ ] 重新提交：`MATERIAL_UPDATED` 可进入 `RESUBMITTED`。
- [ ] 再次 AI Review：重提后重新评估并生成新的 AI report。
- [ ] 人工 Approve/Reject：最终通过或拒绝必须由人工接口确认。
- [ ] 审批历史：人工动作进入 approval history。
- [ ] 多轮 AI report：再次 AI Review 不覆盖旧报告。
- [ ] audit log：补件、重提、AI review 和人工审批保留审计留痕。

## 2. 工程验收

- [ ] Python pytest：`cd agent-service && python -m pytest tests -q`。
- [ ] Java mvn test：`cd backend-service && mvn test`。
- [ ] readiness check：`python scripts/check_demo_readiness.py --skip-services`。
- [ ] Dockerfile 存在：`agent-service/Dockerfile` 和 `backend-service/Dockerfile`。
- [ ] docker compose config：有 Docker CLI 的机器上执行 `docker compose config`。
- [ ] Docker Compose 四服务：`mysql`、`redis`、`agent-service`、`backend-service`。
- [ ] GitHub Actions 可触发：push/PR 自动触发，Actions 页面可手动 Run workflow。
- [ ] README 有启动方式：README 包含 Docker 模式、源码模式和 demo 页面地址。
- [ ] 故障排查文档完整：`docs/TROUBLESHOOTING.md` 覆盖 CI、Docker、端口、MySQL、Agent、Backend、Maven 和 Mock LLM。

## 3. 安全边界验收

- [ ] `.env 未被 git 跟踪`：`git ls-files -- .env agent-service/.env backend-service/.env` 应为空。
- [ ] 默认 Mock LLM：普通测试和 Docker Compose 默认使用 `LLM_PROVIDER=mock`。
- [ ] 不提交真实 API Key：README、docs、脚本和测试只保留占位说明。
- [ ] 不提交真实客户数据：seed/demo 数据只使用脱敏或 mock 信息。
- [ ] AI 不自动最终审批：`APPROVED` / `REJECTED` 仍必须由人工审批接口写入。
- [ ] Docker 默认密码只用于本地 demo：Compose 内默认密码不是生产配置。
- [ ] 补件只保存 mock 摘要：不保存身份证、手机号、征信报告或银行流水原件。

## 4. 面试验收

- [ ] 30 秒介绍：见 `docs/FINAL_INTERVIEW_DELIVERY.md`。
- [ ] 2 分钟介绍：见 `docs/FINAL_INTERVIEW_DELIVERY.md`。
- [ ] 3 分钟 demo：见 `docs/FINAL_DEMO_SCRIPT.md`。
- [ ] 5 分钟 demo：见 `docs/FINAL_DEMO_SCRIPT.md`。
- [ ] 常见追问：覆盖 Java/Python 拆分、Agent、Tool calling、RAG、ML baseline、SeniorReviewAgent、补件复审、Docker/CI 和生产差距。
- [ ] 不能夸大的点：不是真实银行生产系统、不接真实银行数据、不自动放贷。
- [ ] 简历 bullet：见 `docs/RESUME_NOTES.md`，表达应聚焦工程集成和人审边界。

## 5. 当前已知限制

- 本地 Windows 普通 `mvn test` 可能遇到 `target/classes/db/schema.sql` AccessDenied；CI Linux runner 仍使用普通 `mvn test`。
- 当前机器如果没有 Docker CLI，则无法本地执行 `docker compose config` 或 `docker compose up --build`。
- CI 是否成功需要到 GitHub Actions 页面确认；本仓库只保证 workflow 文件可触发并包含静态校验。
- 项目是工程验证和面试项目，不是真实银行生产系统。
- RAG 使用模拟制度库，不是真实银行制度库或生产向量库。
- ML 是 baseline，只作为审批辅助信号，不是生产级风控模型。
