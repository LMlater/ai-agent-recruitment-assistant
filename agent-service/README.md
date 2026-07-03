# agent-service

这是 SmartCreditMultiAgent 的 Python Agent 服务，基于 FastAPI + LangGraph 实现信贷审批辅助工作流。

## 面试演示材料入口

完整面试交付材料请优先看仓库根目录下的文档：

- `../docs/DEMO_GUIDE.md`
- `../docs/ARCHITECTURE.md`
- `../docs/API_WALKTHROUGH.md`
- `../docs/INTERVIEW_SCRIPT.md`
- `../docs/RESUME_NOTES.md`

本地安全演示命令：

```bash
python -m pytest tests -q
python scripts/run_llm_review_demo.py --mock
```

普通测试会强制使用 Mock LLM，不会调用 DashScope/百炼。真实 provider 只允许通过本地环境变量或本地 `.env` 显式开启，`.env` 不能提交。

## 启动服务

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

健康检查：

```bash
curl http://localhost:8001/health
```

审批辅助接口示例：

```bash
curl -X POST http://localhost:8001/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d "{\"application_id\":1,\"customer\":{\"id\":1,\"age\":32,\"monthly_income\":12000,\"work_years\":5,\"existing_debt\":30000,\"overdue_count\":0,\"asset_proof_count\":2},\"loan_application\":{\"amount\":80000,\"term_months\":24,\"purpose\":\"personal consumption\"}}"
```

## 当前 Mock 组件

- RiskAgent 结合确定性规则评分和 Logistic Regression 基线模型概率。
- PolicyAgent 使用本地 TF-IDF 制度检索，制度条款来自模拟 Markdown 文档。
- DecisionAgent 只返回 AI 审批辅助建议，Java 后端仍然要求人工最终审批。

## 第 2 轮：数据与模型基线

这一轮引入公开信贷数据处理链路，不改变 LangGraph 工作流。第二段把训练好的基线模型接入 `RiskAgent`，作为规则评分之外的辅助信号。

```bash
python scripts/download_german_credit.py
python scripts/prepare_credit_dataset.py
python scripts/train_risk_model.py
pytest tests -q
```

生成文件：

- 原始公开数据：`../data/raw/german_credit/german.data`、`../data/raw/german_credit/german.doc`
- 清洗后数据：`../data/processed/credit_cases.csv`、`../data/processed/train.csv`、`../data/processed/test.csv`
- 模型评估指标：`../data/eval/model_metrics.json`
- 评估案例：`../data/eval/model_eval_cases.jsonl`
- 模拟 seed SQL：`../data/seed/generated_customers_seed.sql`、`../data/seed/generated_loan_applications_seed.sql`
- 模型文件：`models/credit_risk_model.joblib`
- 模型元信息：`models/model_metadata.json`

当前 Logistic Regression 基线指标：accuracy 0.6000、precision 0.3936、recall 0.6167、F1 0.4805、ROC-AUC 0.6787。

如果下载脚本无法访问 UCI，请手动把 `german.data` 和 `german.doc` 放到 `../data/raw/german_credit/`，再运行清洗和训练脚本。字段映射、限制和 RiskAgent 融合设计见 `../docs/MODEL_BASELINE.md`。

RiskAgent 融合逻辑：

- 规则评分仍然是主要、可解释的风险基线。
- `RiskModelService.predict_risk()` 输出 `model_risk_probability`、`model_risk_label`、模型版本、特征和解释。
- 最终风险等级取规则和模型中更高的风险等级。
- 最终分数使用 `0.65 * rule_score + 0.35 * model_score`。
- 如果模型不可用，RiskAgent 会 fallback 到规则评分，并记录 `model_used=false` 和 `model_error`。

## 第 3 轮：制度 RAG 基线

这一轮的制度检索完全本地、可复现：

- 文档加载：`app/services/policy_document_loader.py`
- 检索服务：`app/services/policy_retrieval_service.py`
- 数据结构：`app/schemas/policy.py`
- 制度知识库：`knowledge_base/*.md`
- 评估集：`../data/eval/rag_questions.jsonl`
- 评估结果：`../data/eval/rag_eval_results.json`

运行制度检索评估：

```bash
python scripts/evaluate_policy_retrieval.py
```

检索服务会为 `/api/v1/reviews` 返回结构化制度引用。它不会调用真实 LLM、外部 embedding API、Chroma、FAISS 或真实银行制度库。

## 第 4 轮第一段：LLM Provider 抽象

当前服务在 `app/services/llm/` 下提供可替换的 LLM provider 层。默认 provider 是 `MockLLMClient`，所以本地开发和普通单元测试不需要 API Key。`OpenAICompatibleLLMClient` 可以通过环境变量或 `agent-service/.env` 在本地启用 DashScope/百炼；系统环境变量优先于 `.env`。

运行普通测试：

```bash
cd agent-service
python -m pytest tests -q
```

普通测试会通过 `tests/conftest.py` 强制使用 Mock LLM，即使本地 `.env` 开启真实 API，也不会调用 DashScope/百炼。

真实 API smoke test 是手动可选项。只有配置本地 `.env` 后，才直接运行这个测试文件：

```env
LLM_PROVIDER=dashscope
LLM_ENABLE_REAL_API=true
DASHSCOPE_API_KEY=your-key
DASHSCOPE_BASE_URL=your-base-url
DASHSCOPE_MODEL=qwen3.7-plus
```

```bash
python -m pytest tests/test_dashscope_live_smoke.py -q
```

运行可选 LLM review demo：

```bash
python scripts/run_llm_review_demo.py --mock
python scripts/run_llm_review_demo.py --real
python scripts/run_llm_review_demo.py --compact
```

`--mock` 最稳定，不会调用 DashScope/百炼。`--real` 使用本地 DashScope/百炼配置，可能受到网络和模型响应时间影响。`--compact` 使用更短的 demo 输入和更小的生成参数，更适合真实模型演示。真实 LLM 超时时会触发 fallback，这是预期保护机制，不是工作流崩溃。

不要提交 `.env` 或真实 API Key。`.env.example` 只作为占位模板。LLM 只负责生成报告文本，`DecisionAgent` 仍然保留确定性审批建议和人工最终审批边界。

## 第 5 轮：Java + Python 端到端 demo

仓库根目录现在包含 `scripts/run_e2e_credit_review_demo.py`。这个脚本调用 `backend-service`；后端再通过 `/api/v1/reviews` 调用当前 Python 服务，保存 AI report 和 Agent logs，最终审批仍交给 Java 人工审批 API。

运行项目级 demo 前，先启动当前服务：

```bash
cd agent-service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

运行本地安全检查：

```bash
python -m pytest tests -q
python scripts/run_llm_review_demo.py --mock
python scripts/run_llm_review_demo.py --compact
```

然后在 `backend-service` 已启动的前提下，从仓库根目录运行：

```bash
python scripts/run_e2e_credit_review_demo.py
python scripts/run_e2e_credit_review_demo.py --application-id 1
```

普通测试仍然强制 `LLM_PROVIDER=mock` 和 `LLM_ENABLE_REAL_API=false`。真实 DashScope/百炼调用只允许通过本地配置显式开启，相关配置绝不能提交到仓库。
