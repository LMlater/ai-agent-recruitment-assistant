from typing import Any

from app.agents.base import BaseAgent
from app.tools.compliance_tools import SeniorReviewChecklistTool
from app.tools.tool_runner import run_tool


class SeniorReviewAgent(BaseAgent):
    agent_name = "SeniorReviewAgent"

    def __init__(self, senior_review_checklist_tool: SeniorReviewChecklistTool | None = None) -> None:
        self.senior_review_checklist_tool = senior_review_checklist_tool or SeniorReviewChecklistTool()

    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
        tool_output, tool_call = run_tool(
            tool_name=self.senior_review_checklist_tool.tool_name,
            input_summary="Prepare senior manual review checklist for high-risk application",
            operation=lambda: self.senior_review_checklist_tool.run(state),
        )
        return (
            {
                "senior_review_required": tool_output.get("senior_review_required", True),
                "senior_review_reasons": tool_output.get("senior_review_reasons", []),
                "tool_calls": [tool_call.model_dump()],
            },
            "Prepare senior manual review requirements",
            tool_call.output_summary,
        )
