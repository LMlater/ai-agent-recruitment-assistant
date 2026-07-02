# Resume Notes

- Java + Python 双服务架构：Spring Boot 负责业务系统，FastAPI 负责 AI 审批辅助服务。
- LangGraph 多 Agent 工作流：IntakeAgent、RiskAgent、PolicyAgent、ComplianceAgent、DecisionAgent。
- 信贷审批业务流程：客户建档、贷款申请、AI 审批建议、人工审批、审计留痕。
- 风控评分：基于逾期次数、负债收入比、工作年限、申请额度、资产证明的规则评分。
- 制度检索预留：第一轮关键词检索，后续可替换为 Chroma/FAISS RAG。
- Agent 执行日志：每个 Agent 保留输入摘要、输出摘要、耗时和状态。
- 人工审批与审计留痕：AI 只给建议，最终审批必须人工确认。
- 第 1.5 轮工程修复：AI review 只允许 `SUBMITTED` 首次执行，`AI_REVIEWED` 仅用于演示/复评重跑；`APPROVED`、`REJECTED`、`NEED_MORE_INFO` 必须通过人工审批接口进入。
- 第 1.5 轮新增查询链路：AI 报告可通过申请 ID 或报告 ID 查询，Agent 执行日志可通过申请 ID 或 workflow ID 查询。
- 本地演示入口：根 README 与 `backend-service/README.md` 已补充 PowerShell `curl.exe` 流程，包含 init-admin、login、create customer、create loan、submit、AI review、report/log 查询、manual approval、approval history。
- 第 2 轮第一段：基于 UCI German Credit 公开信贷数据集构建风控样本，清洗映射为项目字段，训练 Logistic Regression baseline。
- 模型评估输出 accuracy、precision、recall、F1、ROC-AUC 和混淆矩阵；当前 ROC-AUC 为 0.6787，F1 为 0.4805，Recall 为 0.6167。
- 风控模型只用于审批辅助信号，不做自动决策；第 2 轮第二段已接入 RiskAgent 并与规则评分融合。
- 简历亮点表达：公开数据处理 + 特征映射 + baseline 模型训练 + 模型评估 + artifact 管理 + 审批辅助边界。
- 第 2 轮第二段：RiskAgent 已采用规则评分 + Logistic Regression baseline 概率融合，输出规则原因、模型概率、模型等级、融合风险分和融合风险等级。
- 模型不可用时会降级为规则评分，`risk_assessment` 记录 `model_used=false` 和 `model_error`，避免 AI review 主链路失败。
- DecisionAgent 和 ComplianceAgent 会说明模型只是审批辅助信号，不自动审批，最终审批仍走人工审批接口。
