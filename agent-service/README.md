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

- RiskAgent uses deterministic rules, not a trained risk model.
- PolicyAgent uses keyword matching over local markdown documents, not vector retrieval.
- DecisionAgent returns AI suggestions only; the Java backend must still require human approval.
