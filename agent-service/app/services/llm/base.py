from typing import Protocol


class LLMClient(Protocol):
    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> str:
        ...
