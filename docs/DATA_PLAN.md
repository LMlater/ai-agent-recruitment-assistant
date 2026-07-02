# Data Plan

1. 第一轮使用模拟 seed 数据。
2. 第 2 轮第一段已使用 UCI German Credit / Statlog German Credit 公开数据集作为结构化风控样本。
3. 已清洗并映射为项目可理解字段，生成 `credit_cases.csv`、`train.csv`、`test.csv` 和模拟 seed SQL。
4. 已训练 Logistic Regression baseline，并保存模型 artifact 与评估指标；当前尚未接入 RiskAgent。
5. 后续将构造 RAG 评估集和多 Agent 审批案例评估集。
6. 本项目不使用真实银行客户数据。
7. 本项目不保存真实身份证和手机号，只保存脱敏字段。
8. 模拟制度文档仅用于学习和项目展示，不是真实银行制度。
9. AI 输出只作为审批辅助，不作为自动决策。
