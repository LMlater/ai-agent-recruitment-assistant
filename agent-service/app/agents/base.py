from abc import ABC, abstractmethod
from datetime import datetime
from time import perf_counter
from typing import Any

from app.schemas.review import AgentResult


class BaseAgent(ABC):
    agent_name: str

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        started = datetime.now()
        start_counter = perf_counter()
        try:
            updates, input_summary, output_summary = self.process(state)
            state.update(updates)
            status = "SUCCESS"
            error_message = None
            result = updates
        except Exception as exc:
            status = "FAILED"
            error_message = str(exc)
            input_summary = f"{self.agent_name} execution"
            output_summary = "Agent execution failed"
            result = {}
        ended = datetime.now()
        duration_ms = int((perf_counter() - start_counter) * 1000)
        state.setdefault("agent_results", []).append(
            AgentResult(
                agent_name=self.agent_name,
                status=status,
                input_summary=input_summary,
                output_summary=output_summary,
                error_message=error_message,
                started_at=started,
                ended_at=ended,
                duration_ms=duration_ms,
                result=result,
            )
        )
        return state

    @abstractmethod
    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
        """Return state updates, input summary, and output summary."""
