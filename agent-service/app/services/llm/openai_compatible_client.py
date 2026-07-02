from typing import Any


class LLMClientError(RuntimeError):
    pass


class OpenAICompatibleLLMClient:
    def __init__(
        self,
        api_key: str | None,
        base_url: str | None,
        model: str,
        timeout_seconds: int = 30,
    ) -> None:
        if not api_key:
            raise LLMClientError("OpenAI-compatible LLM API key is not configured.")
        if not base_url:
            raise LLMClientError("OpenAI-compatible LLM base_url is not configured.")

        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout_seconds = timeout_seconds
        try:
            from openai import OpenAI
        except Exception as exc:  # pragma: no cover - exercised only when dependency is missing.
            raise LLMClientError("OpenAI SDK is not installed. Install the openai package.") from exc

        self._client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout_seconds)

    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = self._extract_content(response)
            if not content:
                raise LLMClientError("OpenAI-compatible LLM returned empty content.")
            return content
        except LLMClientError:
            raise
        except Exception as exc:
            raise LLMClientError(
                f"OpenAI-compatible LLM request failed: {self._sanitize_error(exc)}"
            ) from exc

    def _extract_content(self, response: Any) -> str:
        return str(response.choices[0].message.content or "")

    def _sanitize_error(self, exc: Exception) -> str:
        message = str(exc)
        if self.api_key:
            message = message.replace(self.api_key, "[REDACTED_API_KEY]")
        return message
