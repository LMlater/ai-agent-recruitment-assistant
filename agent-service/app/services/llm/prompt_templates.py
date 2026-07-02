import json
import re
from typing import Any


POLICY_CODE_RE = re.compile(r"\b[A-Z]-\d{3}\b")
MAX_POLICY_CONTENT_CHARS = 120
RISK_ASSESSMENT_PROMPT_KEYS = {
    "risk_score",
    "risk_level",
    "rule_reasons",
    "model_used",
    "model_risk_probability",
    "model_risk_level",
    "model_version",
    "fusion_strategy",
}


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
        "risk_assessment": _compact_risk_assessment(context),
        "policy_references": _compact_policy_references(context),
        "allowed_policy_codes": allowed_policy_codes,
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


def _compact_risk_assessment(context: dict[str, Any]) -> dict[str, Any]:
    risk_assessment = context.get("risk_assessment", {})
    compact = {
        key: risk_assessment[key]
        for key in RISK_ASSESSMENT_PROMPT_KEYS
        if key in risk_assessment
    }
    compact.setdefault("risk_score", context.get("risk_score"))
    compact.setdefault("risk_level", context.get("risk_level"))
    return {key: value for key, value in compact.items() if value is not None}


def _compact_policy_references(context: dict[str, Any]) -> list[dict[str, Any]]:
    compact_references: list[dict[str, Any]] = []
    for reference in context.get("policy_references", []):
        if isinstance(reference, dict):
            policy_code = reference.get("policy_code")
            section_title = reference.get("section_title")
            content = reference.get("content", "")
        else:
            policy_code = getattr(reference, "policy_code", None)
            section_title = getattr(reference, "section_title", None)
            content = getattr(reference, "content", "")
        compact_references.append(
            {
                "policy_code": policy_code,
                "section_title": section_title,
                "content": _truncate_text(str(content)),
            }
        )
    return compact_references


def _truncate_text(text: str, limit: int = MAX_POLICY_CONTENT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."
