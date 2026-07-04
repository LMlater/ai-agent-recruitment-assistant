from collections.abc import Callable
from datetime import datetime
from time import perf_counter
from typing import Any

from pydantic import BaseModel


class ToolCall(BaseModel):
    tool_name: str
    status: str
    input_summary: str
    output_summary: str
    started_at: datetime
    ended_at: datetime
    duration_ms: int
    error_message: str | None = None


def run_tool(
    *,
    tool_name: str,
    input_summary: str,
    operation: Callable[[], tuple[dict[str, Any], str]],
) -> tuple[dict[str, Any], ToolCall]:
    started = datetime.now()
    start_counter = perf_counter()
    try:
        output, output_summary = operation()
        status = "SUCCESS"
        error_message = None
    except Exception as exc:
        output = {}
        output_summary = "Tool execution failed"
        status = "FAILED"
        error_message = str(exc)
    ended = datetime.now()
    return output, ToolCall(
        tool_name=tool_name,
        status=status,
        input_summary=input_summary,
        output_summary=output_summary,
        started_at=started,
        ended_at=ended,
        duration_ms=int((perf_counter() - start_counter) * 1000),
        error_message=error_message,
    )
