import json
import re


POLICY_CODE_RE = re.compile(r"\b[A-Z]-\d{3}\b")


class MockLLMClient:
    def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> str:
        del temperature, max_tokens
        content = "\n".join(message.get("content", "") for message in messages)
        policy_codes = sorted(set(POLICY_CODE_RE.findall(content))) or ["未检索到明确制度编号"]
        policy_codes_text = "、".join(policy_codes)
        return json.dumps(
            {
                "summary": (
                    "基于规则评分、ML 模型辅助信号和已检索制度引用，"
                    f"本次审批建议引用 {policy_codes_text}，需由人工复核后确认。"
                ),
                "decision_reasons": [
                    f"制度依据仅来自已检索 policy_references：{policy_codes_text}。",
                    "AI 和 ML 输出仅作为审批辅助，不能自动通过或自动拒绝。",
                    "最终 APPROVED、REJECTED、NEED_MORE_INFO 必须由人工审批接口确认。",
                ],
            },
            ensure_ascii=False,
        )
