from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def _read(p):
    return (PROJECT_ROOT / p).read_text(encoding="utf-8")

def test_round17_1_persisted_tool_calls_parsing():
    f = _read("frontend-service/src/pages/ApplicationDetail.vue")

    assert "parseToolCallsFromOutputSummary" in f
    assert "resolveToolCalls" in f
    assert "tools=" in f
    assert "RiskRuleTool" in f
    assert "结构化 tool_calls 字段" in f
    assert "从 Agent 日志 outputSummary 解析" in f
    assert "材料完整性检查" in f
    assert "规则风控工具" in f
    assert "ReportGenerationTool" in f
    assert "ComplianceGuardrailTool" in f
