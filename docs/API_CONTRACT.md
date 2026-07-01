# API Contract

## Java 调 Python

Endpoint:

```text
POST http://localhost:8001/api/v1/reviews
```

Request:

```json
{
  "application_id": 1,
  "customer": {
    "id": 1,
    "age": 32,
    "monthly_income": 12000,
    "work_years": 5,
    "existing_debt": 30000,
    "overdue_count": 0,
    "asset_proof_count": 2
  },
  "loan_application": {
    "amount": 80000,
    "term_months": 24,
    "purpose": "personal consumption"
  }
}
```

Response:

```json
{
  "workflow_id": "uuid",
  "final_decision": "APPROVE",
  "risk_level": "LOW",
  "risk_score": 100,
  "suggested_amount": 80000,
  "summary": "申请人收入和负债指标相对稳定，未发现明显逾期风险，建议进入人工复核后通过。",
  "agent_results": [
    {
      "agent_name": "RiskAgent",
      "status": "SUCCESS",
      "input_summary": "Run rule-based credit risk scoring",
      "output_summary": "LOW risk with score 100",
      "error_message": null,
      "started_at": "2026-07-01T10:00:00",
      "ended_at": "2026-07-01T10:00:00",
      "duration_ms": 1,
      "result": {}
    }
  ],
  "report": {
    "intake_check": {},
    "risk_assessment": {},
    "policy_references": [],
    "compliance_warnings": [],
    "decision_reasons": [],
    "required_materials": []
  }
}
```

## 后端保存规则

- `loan_application.status` 只更新为 `AI_REVIEWED`。
- `ai_decision_report` 保存最终建议、风险等级、风险分、建议额度和完整报告 JSON。
- `agent_execution_log` 保存每个 Agent 的输入摘要、输出摘要、状态、耗时和错误信息。
- `audit_log` 记录 `AI_REVIEW`。
- AI 不允许直接写入 `APPROVED` 或 `REJECTED`。
