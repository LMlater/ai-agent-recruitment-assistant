# Iteration Log

## 第 1 轮：双服务骨架与 Mock 多 Agent 工作流初始化

- 初始化 Spring Boot backend-service。
- 初始化 FastAPI + LangGraph agent-service。
- 建立客户、贷款申请、AI 审批报告、Agent 执行日志、人工审批、审计日志基础结构。
- 添加 Mock 风控评分、Mock 制度检索和多 Agent 工作流测试。

## 第 1.5 轮：工程修复与演示链路完善

- 收紧 AI review 状态边界：首次执行要求 `SUBMITTED`，允许 `AI_REVIEWED` 为演示或复评再次执行，拒绝 `DRAFT`、`APPROVED`、`REJECTED`、`NEED_MORE_INFO`。
- 收紧普通状态更新接口：`PATCH /api/loan-applications/{id}/status` 不能设置 `APPROVED`、`REJECTED`、`NEED_MORE_INFO`，最终决策必须走人工审批接口并保留审批记录。
- 新增 AI 报告查询接口：`GET /api/loan-applications/{id}/ai-reports`、`GET /api/ai-reports/{reportId}`。
- 新增 Agent 执行日志查询接口：`GET /api/loan-applications/{id}/agent-logs`、`GET /api/agent-workflows/{workflowId}/logs`。
- 补充低、中、高风险 seed 贷款申请，仍为 Mock 数据，不使用真实客户信息。
- 强化 Python Agent 测试：覆盖低、中、高风险、材料缺失、全 Agent 输出完整性。
- 强化 Java 单元测试：覆盖 AI review 状态边界、普通状态更新边界、AI 报告和 Agent 日志查询服务。
- 改进全局异常处理：业务异常保留可读消息，参数校验返回字段信息，系统异常只返回通用错误并记录堆栈。
- 更新根 README 与 backend-service README，补全从初始化管理员到人工审批历史查询的本地演示 curl 流程。

## 第 2 轮第一段：公开信贷数据与风控模型 baseline

- 新增 German Credit 数据下载脚本：`agent-service/scripts/download_german_credit.py`。
- 新增数据清洗和字段映射脚本：`agent-service/scripts/prepare_credit_dataset.py`。
- 生成 `data/processed/credit_cases.csv`、`train.csv`、`test.csv`。
- 新增 Logistic Regression baseline 训练脚本：`agent-service/scripts/train_risk_model.py`。
- 输出模型评估指标：accuracy、precision、recall、F1、ROC-AUC、confusion matrix。
- 保存模型 artifact：`agent-service/models/credit_risk_model.joblib` 和 `model_metadata.json`。
- 新增 `RiskModelService`，可加载模型并输出结构化风险概率、标签、版本、特征和解释。
- 生成低、中、高风险覆盖的模拟 seed SQL 和模型评估案例。
- 当前模型尚未接入 `RiskAgent`，下一轮计划接入为“规则评分 + ML 模型评分”组合。
