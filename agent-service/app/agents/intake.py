from typing import Any

from app.agents.base import BaseAgent
from app.schemas.review import ReviewRequest
from app.tools.intake_tools import MaterialChecklistTool
from app.tools.tool_runner import run_tool


class IntakeAgent(BaseAgent):
    agent_name = "IntakeAgent"

    def __init__(self, material_checklist_tool: MaterialChecklistTool | None = None) -> None:
        self.material_checklist_tool = material_checklist_tool or MaterialChecklistTool()

    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
        request: ReviewRequest = state["request"]
        tool_output, tool_call = run_tool(
            tool_name=self.material_checklist_tool.tool_name,
            input_summary="Check customer basics and loan application materials",
            operation=lambda: self.material_checklist_tool.run(request),
        )
        required_materials = tool_output.get("required_materials", [])
        updates = dict(tool_output)
        if required_materials:
            updates.update(
                {
                    "risk_assessment": {
                        "risk_skipped": True,
                        "skip_reason": "Required materials are incomplete; risk scoring is skipped until valid inputs are supplied.",
                        "risk_score": 0,
                        "risk_level": "HIGH",
                        "suggested_amount": 0,
                    },
                    "risk_score": 0,
                    "risk_level": "HIGH",
                    "suggested_amount": 0,
                }
            )
        updates["tool_calls"] = [tool_call.model_dump()]
        return (
            updates,
            "Check customer basics and loan application materials",
            tool_call.output_summary,
        )
