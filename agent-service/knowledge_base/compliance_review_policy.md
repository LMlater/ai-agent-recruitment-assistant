# Mock Compliance Review Policy

This document is simulated for learning and project demonstration. It is not a real bank policy.
本项目制度文档是模拟制度，只用于学习和工程演示，不代表真实银行内部制度。

## C-001 AI Assistance Only

AI output can only be used as approval assistance and cannot be treated as an automatic decision. AI must not automatically approve, reject, or bypass manual review for personal credit applications.
AI 输出仅可作为审批辅助，不能自动审批、自动拒绝或绕过人工复核。

## C-002 Final Manual Approval Responsibility

Final approval, rejection, or supplementary-material handling must be completed by manual review APIs or reviewer operations. The report may cite policy references, but the reviewer remains responsible for the final decision.
最终通过、拒绝或补件处理必须由人工审批动作完成；系统报告只能提供依据和建议。

## C-003 Audit Trace and Agent Logs

Every review workflow should retain agent execution logs, policy references, model signal details, decision reasons, and audit logs for traceability.
每次审查应保留 Agent 执行日志、制度引用、模型信号、决策原因和审计记录。

## C-004 Data Privacy and Demonstration Boundary

Personal sensitive data should be masked; real identity card numbers, phone numbers, bank internal policies, and production customer data must not be stored in this repository.
项目仅使用公开数据映射和模拟样例，不保存真实银行客户资料、真实证件号、真实手机号或内部制度。
