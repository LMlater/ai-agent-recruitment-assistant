import json
import os
import re
from typing import Any

from app.core.config import settings
from app.services.llm.base import LLMClient
from app.services.llm.llm_client_factory import create_llm_client, current_llm_provider_name
from app.services.llm.mock_llm_client import MockLLMClient
from app.services.llm.openai_compatible_client import OpenAICompatibleLLMClient
from app.services.llm.prompt_templates import build_report_messages


POLICY_CODE_RE = re.compile(r"\b[A-Z]-\d{3}\b")


class ReportGenerationService:
    def __init__(self, llm_client: LLMClient | None = None, llm_provider: str | None = None) -> None:
        self.llm_client = llm_client or create_llm_client()
        self.llm_provider = llm_provider or self._infer_llm_provider(self.llm_client)

    def generate(self, context: dict[str, Any]) -> dict[str, Any]:
        messages = build_report_messages(context)
        try:
            raw_text = self.llm_client.generate(
                messages,
                temperature=self._llm_temperature(),
                max_tokens=self._llm_max_tokens(),
            )
            parsed = self._parse_json(raw_text)
            self._validate_policy_codes(parsed, context)
            return {
                "summary": str(parsed["summary"]),
                "decision_reasons": self._ensure_required_reasons(
                    context,
                    [str(reason) for reason in parsed["decision_reasons"]]
                    + [str(reason) for reason in context.get("decision_reasons", [])],
                ),
                "llm_used": True,
                "llm_provider": self.llm_provider,
                "llm_error": None,
            }
        except Exception as exc:
            return self._fallback_result(context, str(exc))

    def _parse_json(self, raw_text: str) -> dict[str, Any]:
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").strip()
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        payload = json.loads(cleaned)
        if not isinstance(payload, dict):
            raise ValueError("LLM response JSON must be an object.")
        if not isinstance(payload.get("summary"), str):
            raise ValueError("LLM response summary must be a string.")
        if not isinstance(payload.get("decision_reasons"), list):
            raise ValueError("LLM response decision_reasons must be a list.")
        return payload

    def _validate_policy_codes(self, parsed: dict[str, Any], context: dict[str, Any]) -> None:
        allowed_codes = set(self._policy_codes(context))
        generated_text = parsed["summary"] + "\n" + "\n".join(str(item) for item in parsed["decision_reasons"])
        generated_codes = set(POLICY_CODE_RE.findall(generated_text))
        unknown_codes = generated_codes - allowed_codes
        if unknown_codes:
            raise ValueError(f"LLM response referenced unknown policy codes: {sorted(unknown_codes)}")

    def _fallback_result(self, context: dict[str, Any], error: str | None) -> dict[str, Any]:
        return {
            "summary": self._fallback_summary(context),
            "decision_reasons": self._ensure_required_reasons(
                context,
                list(context.get("decision_reasons", [])),
            ),
            "llm_used": False,
            "llm_provider": self.llm_provider,
            "llm_error": error,
        }

    def _fallback_summary(self, context: dict[str, Any]) -> str:
        base_summary = str(context.get("summary") or "系统已生成确定性审批辅助摘要。")
        policy_codes = self._policy_codes(context)
        code_text = "、".join(policy_codes) if policy_codes else "无明确制度编号"
        return f"{base_summary} 制度依据：{code_text}。AI/ML 仅作辅助，最终需人工审批确认。"

    def _ensure_required_reasons(self, context: dict[str, Any], reasons: list[str]) -> list[str]:
        merged = [reason for reason in reasons if reason]
        risk_assessment = context.get("risk_assessment", {})
        for reason in risk_assessment.get("rule_reasons", []):
            self._append_unique(merged, str(reason))
        if risk_assessment.get("model_used"):
            self._append_unique(
                merged,
                "ML model signal: "
                f"probability={risk_assessment.get('model_risk_probability')}, "
                f"level={risk_assessment.get('model_risk_level')}, "
                f"version={risk_assessment.get('model_version')}.",
            )
        else:
            self._append_unique(
                merged,
                "ML model unavailable; rule scoring fallback was used. "
                f"Reason: {risk_assessment.get('model_error')}",
            )
        policy_codes = self._policy_codes(context)
        if policy_codes:
            self._append_unique(merged, f"Policy references: {', '.join(policy_codes)}.")
        self._append_unique(
            merged,
            "AI and ML outputs are approval assistance only; final approval must remain manual.",
        )
        return merged

    def _policy_codes(self, context: dict[str, Any]) -> list[str]:
        codes: list[str] = []
        for reference in context.get("policy_references", []):
            code = reference.get("policy_code") if isinstance(reference, dict) else getattr(reference, "policy_code", None)
            if code and POLICY_CODE_RE.fullmatch(str(code)):
                codes.append(str(code))
        return sorted(set(codes))

    def _append_unique(self, reasons: list[str], reason: str) -> None:
        if reason not in reasons:
            reasons.append(reason)

    def _llm_temperature(self) -> float:
        return float(os.getenv("LLM_TEMPERATURE", str(settings.llm_temperature)))

    def _llm_max_tokens(self) -> int:
        return int(os.getenv("LLM_MAX_TOKENS", str(settings.llm_max_tokens)))

    def _infer_llm_provider(self, llm_client: LLMClient) -> str:
        if isinstance(llm_client, MockLLMClient):
            return "mock"
        if isinstance(llm_client, OpenAICompatibleLLMClient):
            return current_llm_provider_name()
        return current_llm_provider_name()
