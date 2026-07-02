# Mock Risk Control Policy

This document is simulated for learning and project demonstration. It is not a real bank policy.
本项目制度文档是模拟制度，只用于学习和工程演示，不代表真实银行内部制度。

## R-001 Debt-to-Income Ratio Control

Debt-to-income ratio is a key repayment-capacity indicator. Debt-to-income ratio above 40% should receive attention, above 60% should trigger medium-risk manual review, and above 80% should be treated as high repayment pressure.
债务收入比是偿债能力核心指标；债务收入比较高时，应结合贷款金额、收入证明和人工复核判断，不得单靠模型通过。

## R-002 Overdue Records and Credit History

Overdue records should reduce the mock risk score. Multiple overdue records, recent overdue behavior, or severe overdue history should trigger high-risk manual review before any final business decision.
存在多次逾期记录时，应降低风险评分并进入高风险人工复核；逾期风险不能被资产证明或模型低风险结果直接抵消。

## R-003 Medium and High Risk Manual Review

Medium-risk applications should request additional review of repayment capacity and materials. High-risk customers must be reviewed by a human reviewer before any final approval, rejection, or supplementary-material conclusion.
中风险申请应补充核验收入、负债、用途和资产材料；高风险申请必须人工复核后才能形成最终业务结论。

## R-004 Rule and ML Model Fusion Guardrail

Rule reasons and ML model signals are auxiliary risk indicators. If rule and model levels differ, the workflow should consider the higher risk level and keep the model probability, version, and explanation in the report.
规则评分和机器学习模型均为辅助信号；当模型提示中高风险时，应在报告中保留模型概率、版本、解释和融合策略。
