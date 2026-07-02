# Validation Log

## 第 6 轮演示包装与面试交付版验证

日期：2026-07-02

### readiness script

```powershell
python scripts\check_demo_readiness.py
```

结果：脚本正常输出 JSON，没有 Python stack trace。当前未启动 backend-service 和 agent-service，因此返回退出码 `1`，`ok=false`，文件检查全部为 `true`，安全检查显示 `env_file_tracked=false`、`prints_api_key=false`，服务检查显示：

```json
{
  "backend": {"reachable": false},
  "agent": {"reachable": false}
}
```

这是真实环境状态记录，未伪造双服务联调成功。

```powershell
python scripts\check_demo_readiness.py --skip-services
```

结果：通过，退出码 `0`。输出摘要：`ok=true`，关键文件齐全，`.env` 未被 git 跟踪，readiness 输出不包含真实 API Key。

### agent-service

```powershell
cd agent-service
$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests -q -p no:cacheprovider
```

结果：通过。输出摘要：`57 passed, 1 skipped, 1 warning in 3.67s`。跳过项为真实 DashScope/Bailian smoke test，普通测试仍强制 Mock，不调用真实百炼。

### backend-service

```powershell
cd backend-service
mvn -q "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" test
```

结果：通过，退出码 `0`。继续使用仓库内 `.m2` 作为 Maven 本地仓库路径，以避免当前沙箱默认外部 Maven 仓库路径访问拒绝问题。

### 第 6 轮安全检查

- `.env` 未提交，`.gitignore` 仍包含 `.env`。
- 文档只包含本地 demo admin 示例和 API Key 占位说明，不包含真实 API Key。
- `scripts/check_demo_readiness.py` 不读取、不打印真实 LLM 密钥。
- 本轮未调用真实百炼，未修改 Java 数据库表结构，未让 AI 自动审批最终状态。

### 下一步建议

- 面试前先运行 `python scripts\check_demo_readiness.py --skip-services` 检查文件和安全状态。
- 启动 agent-service 和 backend-service 后，再运行 `python scripts\check_demo_readiness.py` 验证服务可达。
- 真正演示 E2E 前按 `docs/DEMO_GUIDE.md` 的顺序执行，不要把服务未启动状态说成联调成功。

## 第 5 轮端到端演示闭环验证

日期：2026-07-02

### agent-service

```powershell
cd agent-service
$env:PYTHONDONTWRITEBYTECODE='1'; python -m pytest tests -q -p no:cacheprovider
```

结果：通过。输出摘要：`53 passed, 1 skipped, 1 warning in 3.50s`。跳过项为真实 DashScope/Bailian smoke test，普通测试未调用真实百炼。

```powershell
python scripts\run_llm_review_demo.py --mock
```

结果：通过。输出包含 `workflow_id`、`final_decision=NEED_MORE_INFO`、`risk_level=MEDIUM`、`risk_score=78`、policy codes，以及 `decision_report_generation.llm_provider=mock`。未输出 API Key。

```powershell
$env:LLM_PROVIDER='mock'; $env:LLM_ENABLE_REAL_API='false'; python scripts\run_llm_review_demo.py --compact
```

结果：通过。输出包含 `workflow_id`、`final_decision=APPROVE`、`risk_level=LOW`、`risk_score=97`、policy codes，以及 `decision_report_generation.llm_provider=mock`。为避免本地环境变量触发真实 provider，本次自动验证显式覆盖为 Mock。

### backend-service

```powershell
cd backend-service
mvn -q "-Dmaven.repo.local=D:\PythonProject\ai-agent-recruitment-assistant\.m2\repository" test
```

结果：通过，退出码 `0`。使用仓库内 `.m2` 作为 Maven 本地仓库路径；默认外部 Maven 仓库路径在当前沙箱中曾出现访问拒绝。

覆盖点：

- Java 可以反序列化 Python `/api/v1/reviews` 返回中的结构化 `policy_references`。
- Java 可以保留 `AgentResult.result.decision_report_generation` 嵌套对象。
- `AgentReviewService` 保存 `report_json` 时保留结构化制度引用。
- `AgentReviewService` 将 DecisionAgent 的 `llm_used`、`llm_provider`、`llm_error` 摘要保存到现有 `agent_execution_log.output_summary`。
- AI review 后状态仍写入 `AI_REVIEWED`，不直接写入 `APPROVED` 或 `REJECTED`。
- `DRAFT`、`APPROVED`、`REJECTED`、`NEED_MORE_INFO` 等状态会拒绝 AI review。

### project-level E2E demo script

```powershell
python scripts\run_e2e_credit_review_demo.py --application-id 1
```

结果：当前未启动 backend-service，因此脚本按预期返回清晰错误并退出 `1`：

```json
{
  "ok": false,
  "error": "Cannot connect to backend at http://localhost:8080. Start backend-service first and check BACKEND_BASE_URL.",
  "hint": "Start backend-service and agent-service first; use --application-id with a SUBMITTED or AI_REVIEWED application if needed."
}
```

未伪造端到端服务联调成功。实际联调前需要先启动：

```powershell
cd agent-service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

```powershell
cd backend-service
mvn spring-boot:run
```

然后从仓库根目录运行：

```powershell
python scripts\run_e2e_credit_review_demo.py
python scripts\run_e2e_credit_review_demo.py --application-id 1
python scripts\run_e2e_credit_review_demo.py --application-id 1 --manual-decision approve
```

### safety check

- `.env` 未提交，`.gitignore` 仍包含 `.env`。
- 文档只包含占位符和命令示例，不包含真实 API Key。
- demo 输出不打印 `DASHSCOPE_API_KEY`。
- 普通 Python 测试通过 `tests/conftest.py` 强制 Mock LLM。
- 本轮未修改 Java 数据库表结构。
