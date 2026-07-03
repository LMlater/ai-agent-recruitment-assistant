from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_BASE = REPO_ROOT / "agent-service" / "knowledge_base"


def test_mock_policy_documents_are_chinese_first_for_visual_demo():
    expected_titles = {
        "risk_control_policy.md": [
            "## R-004 规则与机器学习模型融合边界",
        ],
        "material_review_policy.md": [
            "## M-003 资产证明复核要求",
        ],
        "personal_credit_policy.md": [
            "## P-002 收入证明与稳定工作年限",
            "## P-003 贷款金额、收入比例与还款能力",
            "## P-004 个人信贷审批边界",
        ],
        "compliance_review_policy.md": [
            "## C-001 AI 辅助定位",
            "## C-002 最终人工审批责任",
        ],
    }

    for filename, titles in expected_titles.items():
        text = (KNOWLEDGE_BASE / filename).read_text(encoding="utf-8")
        assert "模拟制度" in text
        assert "只用于学习和工程演示" in text
        for title in titles:
            assert title in text
