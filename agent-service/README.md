# agent-service

FastAPI + LangGraph service for the SmartCreditMultiAgent first-round mock credit review workflow.

## Interview Demo Package

For the full interview delivery package, start from the repository root docs:

- `../docs/DEMO_GUIDE.md`
- `../docs/ARCHITECTURE.md`
- `../docs/API_WALKTHROUGH.md`
- `../docs/INTERVIEW_SCRIPT.md`
- `../docs/RESUME_NOTES.md`

Safe local Agent demo:

```bash
python -m pytest tests -q
python scripts/run_llm_review_demo.py --mock
```

Ordinary tests force Mock LLM and do not call DashScope/Bailian. Real provider usage is opt-in through local environment configuration only, and `.env` must not be committed.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Health check:

```bash
curl http://localhost:8001/health
```

Review endpoint:

```bash
curl -X POST http://localhost:8001/api/v1/reviews \
  -H "Content-Type: application/json" \
  -d "{\"application_id\":1,\"customer\":{\"id\":1,\"age\":32,\"monthly_income\":12000,\"work_years\":5,\"existing_debt\":30000,\"overdue_count\":0,\"asset_proof_count\":2},\"loan_application\":{\"amount\":80000,\"term_months\":24,\"purpose\":\"personal consumption\"}}"
```

## Current Mock Pieces

- RiskAgent combines deterministic rules with the Logistic Regression baseline probability signal.
- PolicyAgent uses local TF-IDF policy retrieval over structured mock markdown clauses.
- DecisionAgent returns AI suggestions only; the Java backend must still require human approval.

## Round 2 Data And Model Baseline

This round adds public-credit-data infrastructure without changing the LangGraph workflow. The second segment connects the trained baseline to `RiskAgent` as an auxiliary signal while preserving deterministic rule scoring.

```bash
python scripts/download_german_credit.py
python scripts/prepare_credit_dataset.py
python scripts/train_risk_model.py
pytest tests -q
```

Generated files:

- Raw public data: `../data/raw/german_credit/german.data`, `../data/raw/german_credit/german.doc`
- Processed data: `../data/processed/credit_cases.csv`, `../data/processed/train.csv`, `../data/processed/test.csv`
- Metrics: `../data/eval/model_metrics.json`
- Eval cases: `../data/eval/model_eval_cases.jsonl`
- Seed SQL: `../data/seed/generated_customers_seed.sql`, `../data/seed/generated_loan_applications_seed.sql`
- Model artifact: `models/credit_risk_model.joblib`
- Model metadata: `models/model_metadata.json`

Current Logistic Regression baseline metrics: accuracy 0.6000, precision 0.3936, recall 0.6167, F1 0.4805, ROC-AUC 0.6787.

If the download script cannot access UCI, manually place `german.data` and `german.doc` under `../data/raw/german_credit/`, then run the prepare and training scripts. See `../docs/MODEL_BASELINE.md` for mapping logic, limitations, and the RiskAgent fusion design.

RiskAgent fusion behavior:

- Rule scoring remains the primary explainable baseline.
- `RiskModelService.predict_risk()` provides `model_risk_probability`, `model_risk_label`, version, features, and explanation.
- Final level takes the higher risk level from rule and model.
- Final score uses `0.65 * rule_score + 0.35 * model_score`.
- If the model is unavailable, RiskAgent falls back to rule scoring and records `model_used=false` plus `model_error`.

## Round 3 Policy RAG Baseline

Policy retrieval is fully local and deterministic in this round:

- Loader: `app/services/policy_document_loader.py`
- Retriever: `app/services/policy_retrieval_service.py`
- Schema: `app/schemas/policy.py`
- Knowledge base: `knowledge_base/*.md`
- Eval set: `../data/eval/rag_questions.jsonl`
- Eval output: `../data/eval/rag_eval_results.json`

Run retrieval evaluation:

```bash
python scripts/evaluate_policy_retrieval.py
```

The retriever returns structured policy references for `/api/v1/reviews`. It does not call a real LLM, external embedding API, Chroma, FAISS, or real bank policy source.

## 第 4 轮第一段：LLM Provider 抽象

The service now has a replaceable LLM provider layer under `app/services/llm/`. The default provider is `MockLLMClient`, so local development and unit tests do not require an API key. `OpenAICompatibleLLMClient` can be enabled locally for DashScope/Bailian through environment variables or `agent-service/.env`; shell environment variables take precedence.

Run ordinary tests:

```bash
cd agent-service
python -m pytest tests -q
```

Ordinary tests force Mock LLM settings through `tests/conftest.py`, so they do not call DashScope/Bailian even if local `.env` enables real API access.

The live smoke test is opt-in and should be run directly after configuring local `.env`:

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

Run the optional LLM review demo:

```bash
python scripts/run_llm_review_demo.py --mock
python scripts/run_llm_review_demo.py --real
python scripts/run_llm_review_demo.py --compact
```

`--mock` is stable and never calls DashScope/Bailian. `--real` uses the local DashScope/Bailian configuration and may be affected by network or model latency. `--compact` uses shorter demo input and smaller generation defaults for real-model demos. If a real LLM call times out, fallback is expected protection rather than a workflow crash.

Do not commit `.env` or a real API key. Use `.env.example` as the placeholder template and keep the LLM as report text generation only; `DecisionAgent` still preserves the deterministic final decision and manual approval boundary.

## Round 5 Java + Python E2E Demo

The repository root now contains `scripts/run_e2e_credit_review_demo.py`. That script talks to `backend-service`; the backend calls this service through `/api/v1/reviews`, stores the AI report, stores Agent logs, and then leaves final approval to the Java manual approval APIs.

Start this service before running the project-level demo:

```bash
cd agent-service
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Run safe local checks:

```bash
python -m pytest tests -q
python scripts/run_llm_review_demo.py --mock
python scripts/run_llm_review_demo.py --compact
```

Then, from the repository root and with `backend-service` running:

```bash
python scripts/run_e2e_credit_review_demo.py
python scripts/run_e2e_credit_review_demo.py --application-id 1
```

Ordinary tests still force `LLM_PROVIDER=mock` and `LLM_ENABLE_REAL_API=false`. Real DashScope/Bailian calls remain opt-in through local environment configuration and must never be committed to the repository.
