# agent-service

FastAPI + LangGraph service for the SmartCreditMultiAgent first-round mock credit review workflow.

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
- PolicyAgent uses keyword matching over local markdown documents, not vector retrieval.
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
