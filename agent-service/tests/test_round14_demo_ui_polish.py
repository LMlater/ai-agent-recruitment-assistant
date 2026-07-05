from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _read_repo_text(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_round14_demo_page_contains_interview_polish_anchors():
    demo_html = _read_repo_text("backend-service/src/main/resources/static/demo.html")

    for expected in (
        "SmartCreditMultiAgent",
        "Human-in-the-loop",
        "Tool Trace",
        "Policy RAG",
        "Real LLM Report",
        "重新开始演示",
        "真实 LLM 可能需要 30-90 秒",
        "已等待",
        "AI Review 完成，已生成 Agent Trace 和审批辅助报告",
        "SeniorReviewAgent",
        "ReportGenerationTool",
        "APPROVED / REJECTED",
        "该申请已完成最终人工审批，不能继续补件或重复审批",
    ):
        assert expected in demo_html


def test_round14_demo_page_keeps_sensitive_values_out_of_static_html():
    demo_html = _read_repo_text("backend-service/src/main/resources/static/demo.html")

    forbidden_fragments = (
        "sk-",
        "DASHSCOPE_API_KEY=",
        "百炼 API Key",
        "your-real-api-key",
    )
    for forbidden in forbidden_fragments:
        assert forbidden not in demo_html
