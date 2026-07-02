from typing import Any

from app.agents.base import BaseAgent


class DecisionAgent(BaseAgent):
    agent_name = "DecisionAgent"

    def process(self, state: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
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

        return (
            {
                "final_decision": final_decision,
                "summary": summary,
                "decision_reasons": reasons,
            },
            "Summarize upstream agent outputs",
            f"Generated {final_decision} recommendation",
        )
