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

Run ordinary development tests:

```bash
cd agent-service
python -m pytest tests -q
```

Ordinary tests are isolated by `tests/conftest.py`; they force `LLM_PROVIDER=mock` and `LLM_ENABLE_REAL_API=false`, so they do not call DashScope/Bailian even when a local `.env` enables real API access.

The real API smoke test is opt-in and should be run by targeting the smoke file directly:

```bash
cd agent-service
python -m pytest tests/test_dashscope_live_smoke.py -q
```

Use local configuration such as:

```env
LLM_PROVIDER=dashscope
LLM_ENABLE_REAL_API=true
DASHSCOPE_API_KEY=your-key
DASHSCOPE_BASE_URL=your-base-url
DASHSCOPE_MODEL=qwen3.7-plus
```

Only run the smoke test after setting `DASHSCOPE_API_KEY` and `DASHSCOPE_BASE_URL` locally. The test sends a short request, checks only that the result is non-empty, and does not print the key or full response.

## Review Demo

Run the optional end-to-end review demo:

```bash
cd agent-service
python scripts/run_llm_review_demo.py
```

When `LLM_ENABLE_REAL_API=false`, the demo uses `MockLLMClient`. When `LLM_ENABLE_REAL_API=true` and local DashScope/Bailian key/base URL settings are valid, the demo uses the OpenAI-compatible client. The output includes workflow id, final decision, risk score, policy codes, summary, decision reasons, and `decision_report_generation` metadata, but never prints an API key.

## Fallback

If the LLM returns non-JSON text, references an unknown policy code, or raises an exception, `ReportGenerationService` falls back to deterministic report text. `DecisionAgent` still returns a successful agent result, preserves the original final decision, and records report generation metadata in `decision_report_generation`.

## Future Work

Later rounds can make the report schema richer, add stricter JSON schema validation, and support more providers. Those changes should keep the same approval boundary: LLM output is explanatory text only, while manual approval remains the final authority.
