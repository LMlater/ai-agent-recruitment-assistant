from typing import Any

from app.agents.base import BaseAgent
from app.tools.compliance_tools import ComplianceGuardrailTool
from app.tools.tool_runner import run_tool


class ComplianceAgent(BaseAgent):
    agent_name = "ComplianceAgent"

    def __init__(self, compliance_guardrail_tool: ComplianceGuardrailTool | None = None) -> None:
        self.compliance_guardrail_tool = compliance_guardrail_tool or ComplianceGuardrailTool()

    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
        tool_output, tool_call = run_tool(
            tool_name=self.compliance_guardrail_tool.tool_name,
            input_summary="Check AI decision boundaries and audit requirements",
            operation=lambda: self.compliance_guardrail_tool.run(state),
        )
        return (
            {
                "compliance_warnings": tool_output.get("compliance_warnings", []),
                "tool_calls": [tool_call.model_dump()],
            },
            "Check AI decision boundaries and audit requirements",
            tool_call.output_summary,
        )
