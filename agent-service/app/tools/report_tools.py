from typing import Any

from app.services.report_generation_service import ReportGenerationService


class ReportGenerationTool:
    tool_name = "ReportGenerationTool"

    def __init__(self, report_generation_service: ReportGenerationService | None = None) -> None:
        self.report_generation_service = report_generation_service or ReportGenerationService()

    def run(self, context: dict[str, Any]) -> tuple[dict[str, Any], str]:
        report_generation = self.report_generation_service.generate(context)
        return report_generation, (
            "Generated report using LLM provider"
            if report_generation.get("llm_used")
            else "Generated report using deterministic fallback"
        )
