# LLM Integration

## Why Add LLM After RAG

The existing workflow already has rule scoring, ML risk signals, and local policy retrieval. The LLM layer is added only to turn those structured signals into a more natural AI-assisted review report. It does not replace the deterministic risk decision path.

## Boundary

The LLM is a report generation component, not an approval authority. It can only organize text from the given risk assessment, model output, and `policy_references`. It must not invent policy clauses, change `final_decision`, change `risk_score`, change `risk_level`, or bypass manual approval.

Final approval states such as `APPROVED`, `REJECTED`, and `NEED_MORE_INFO` still have to be confirmed by the manual approval API.

## Provider Design

`agent-service/app/services/llm/base.py` defines the `LLMClient` protocol:

```python
generate(messages, temperature=0.2, max_tokens=1200) -> str
```

`ReportGenerationService` depends on that protocol instead of a concrete vendor SDK. This keeps the workflow replaceable:

- `MockLLMClient` for local development and unit tests.
- `OpenAICompatibleLLMClient` for DashScope/Bailian OpenAI-compatible chat completions.
- `llm_client_factory.py` selects the provider from environment variables.

## MockLLMClient

`MockLLMClient` never calls an external service. It returns stable JSON containing a summary and decision reasons, including manual review and AI/ML assistance boundaries. It is the default provider so ordinary tests and local development do not require any API key.

## OpenAI-Compatible Client

`OpenAICompatibleLLMClient` uses the OpenAI-compatible Chat Completions interface. It reads `api_key`, `base_url`, `model`, and timeout from configuration. Request failures are wrapped in `LLMClientError`, and the API key is redacted from exception messages.

## Configuration

Use environment variables or a local `agent-service/.env` file. The service loads that file at startup with `python-dotenv`, and existing shell environment variables take precedence. Do not commit `.env`.

```env
LLM_PROVIDER=mock
LLM_ENABLE_REAL_API=false

DASHSCOPE_API_KEY=replace-with-your-api-key
DASHSCOPE_BASE_URL=https://replace-with-your-bailian-compatible-mode-base-url/v1
DASHSCOPE_MODEL=qwen-plus

LLM_TIMEOUT_SECONDS=30
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=1200
```

Default behavior is safe:

- `LLM_PROVIDER=mock`
- `LLM_ENABLE_REAL_API=false`
- Empty `DASHSCOPE_API_KEY` falls back to mock
- Unknown providers fall back to mock

## DashScope/Bailian Setup

For local smoke testing only, configure the API key outside the repository, for example in `agent-service/.env` or the shell environment. The repository must not contain a real key, workspace id, or secret-bearing log.

The base URL must come from environment configuration. The checked-in `.env.example` only contains placeholders.

## Tests

Run ordinary tests:

```bash
cd agent-service
pytest tests -q
```

The real API smoke test is opt-in and skipped by default:

```bash
cd agent-service
LLM_ENABLE_REAL_API=true pytest tests/test_dashscope_live_smoke.py -q
```

Only run the smoke test after setting `DASHSCOPE_API_KEY` locally. The test sends a short request and does not print the key.

## Fallback

If the LLM returns non-JSON text, references an unknown policy code, or raises an exception, `ReportGenerationService` falls back to deterministic report text. `DecisionAgent` still returns a successful agent result, preserves the original final decision, and records report generation metadata in `decision_report_generation`.

## Future Work

Later rounds can make the report schema richer, add stricter JSON schema validation, and support more providers. Those changes should keep the same approval boundary: LLM output is explanatory text only, while manual approval remains the final authority.
