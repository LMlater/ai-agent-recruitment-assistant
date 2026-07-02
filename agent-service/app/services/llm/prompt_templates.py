import json
import re
from typing import Any


POLICY_CODE_RE = re.compile(r"\b[A-Z]-\d{3}\b")


SYSTEM_PROMPT = """你是信贷审批辅助系统中的报告生成组件，不是最终审批人。
你只能基于给定的结构化风险评估、模型信号和制度引用生成报告。
你不能编造不存在的制度条款。
你不能输出真实审批结论，只能输出人工复核建议。
你不能要求自动通过或自动拒绝。
最终 APPROVED、REJECTED、NEED_MORE_INFO 必须由人工审批接口确认。
请只返回合法 JSON，格式为 {"summary":"...","decision_reasons":["..."]}。"""


def build_report_messages(context: dict[str, Any]) -> list[dict[str, str]]:
    allowed_policy_codes = _policy_codes(context)
    prompt_payload = {
        "final_decision_for_reference_only": context.get("final_decision"),
        "risk_level": context.get("risk_level"),
        "risk_score": context.get("risk_score"),
        "suggested_amount": context.get("suggested_amount"),
        "risk_assessment": context.get("risk_assessment", {}),
        "policy_references": context.get("policy_references", []),
        "allowed_policy_codes": allowed_policy_codes,
        "compliance_warnings": context.get("compliance_warnings", []),
        "required_materials": context.get("required_materials", []),
        "base_summary": context.get("summary"),
        "base_decision_reasons": context.get("decision_reasons", []),
    }
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "请基于以下 JSON 生成审批辅助报告。只能引用 allowed_policy_codes 中出现的制度编号：\n"
                + json.dumps(prompt_payload, ensure_ascii=False, indent=2)
            ),
        },
    ]


def _policy_codes(context: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    for reference in context.get("policy_references", []):
        code = reference.get("policy_code") if isinstance(reference, dict) else getattr(reference, "policy_code", None)
        if code and POLICY_CODE_RE.fullmatch(str(code)):
            codes.append(str(code))
    return sorted(set(codes))
