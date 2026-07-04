from typing import Any

from app.agents.base import BaseAgent
from app.services.report_generation_service import ReportGenerationService
from app.tools.report_tools import ReportGenerationTool
from app.tools.tool_runner import ToolCall, run_tool


class DecisionAgent(BaseAgent):
    agent_name = "DecisionAgent"

    def __init__(self, report_generation_service: ReportGenerationService | None = None) -> None:
        self.report_generation_tool = ReportGenerationTool(report_generation_service)

    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
        final_decision, summary, reasons = self._build_deterministic_decision(state)
        report_generation, tool_call = self._generate_report_with_fallback(
            state,
            final_decision,
            summary,
            reasons,
        )
        return (
            {
                "final_decision": final_decision,
                "summary": report_generation["summary"],
                "decision_reasons": report_generation["decision_reasons"],
                "decision_report_generation": {
                    "llm_used": report_generation["llm_used"],
                    "llm_provider": report_generation["llm_provider"],
                    "llm_error": report_generation["llm_error"],
                },
                "tool_calls": [tool_call.model_dump()],
            },
            "Summarize upstream agent outputs",
            self._output_summary(final_decision, report_generation),
        )

    def _build_deterministic_decision(self, state: dict[str, Any]) -> tuple[str, str, list[str]]:
        risk_level = state["risk_level"]
        required_materials = state.get("required_materials", [])
        risk_assessment = state["risk_assessment"]
        reasons = list(risk_assessment.get("rule_reasons", risk_assessment.get("reasons", [])))

        if risk_assessment.get("model_used"):
            reasons.append(
                "ML model signal: "
                f"probability={risk_assessment.get('model_risk_probability')}, "
                f"level={risk_assessment.get('model_risk_level')}, "
                f"version={risk_assessment.get('model_version')}."
            )
        else:
            reasons.append(
                "ML model unavailable; rule scoring fallback was used. "
                f"Reason: {risk_assessment.get('model_error')}"
            )
        if state.get("senior_review_required"):
            reasons.append("Senior manual review is required before any final business decision.")
            reasons.extend(state.get("senior_review_reasons", []))
        reasons.append("AI and ML outputs are approval assistance only; final approval must remain manual.")

        if required_materials:
            final_decision = "NEED_MORE_INFO"
            summary = "申请材料存在缺失或异常，建议要求补充材料后再进入人工复核。"
            reasons.append("Material completeness check requires follow-up.")
        elif risk_level == "LOW":
            final_decision = "APPROVE"
            summary = "申请人收入和负债指标相对稳定，未发现明显逾期风险，建议进入人工复核后通过。"
            reasons.append("Low mock risk score supports approval recommendation.")
        elif risk_level == "MEDIUM":
            final_decision = "NEED_MORE_INFO"
            summary = "申请人存在一定负债或额度压力，建议补充收入、资产或用途材料后由人工复核。"
            reasons.append("Medium mock risk score requires extra manual attention.")
        else:
            final_decision = "REJECT"
            summary = "申请人存在较高逾期、负债或额度风险，AI 建议人工复核时重点考虑拒绝。"
            reasons.append("High mock risk score indicates rejection recommendation.")

        return final_decision, summary, reasons

    def _generate_report_with_fallback(
        self,
        state: dict[str, Any],
        final_decision: str,
        summary: str,
        reasons: list[str],
    ) -> tuple[dict[str, Any], ToolCall]:
        context = {
            "final_decision": final_decision,
            "risk_level": state.get("risk_level"),
            "risk_score": state.get("risk_score"),
            "suggested_amount": state.get("suggested_amount"),
            "summary": summary,
            "decision_reasons": reasons,
            "risk_assessment": state.get("risk_assessment", {}),
            "policy_references": state.get("policy_references", []),
            "compliance_warnings": state.get("compliance_warnings", []),
            "required_materials": state.get("required_materials", []),
            "senior_review_required": state.get("senior_review_required", False),
            "senior_review_reasons": state.get("senior_review_reasons", []),
        }
        report_generation, tool_call = run_tool(
            tool_name=self.report_generation_tool.tool_name,
            input_summary="Generate manual-review report from structured agent state",
            operation=lambda: self.report_generation_tool.run(context),
        )
        if not report_generation.get("summary"):
            report_generation = {
                "summary": summary,
                "decision_reasons": reasons,
                "llm_used": False,
                "llm_provider": "fallback",
                "llm_error": tool_call.error_message,
            }
        return report_generation, tool_call

    def _output_summary(self, final_decision: str, report_generation: dict[str, Any]) -> str:
        if report_generation.get("llm_used"):
            return f"Generated {final_decision} recommendation using LLM report generation"
        return f"Generated {final_decision} recommendation using deterministic fallback"
