# 第 2 轮第一段：公开信贷数据与风控模型 baseline

## 数据来源

本轮使用 UCI German Credit / Statlog German Credit 公开数据集：

- `german.data`：结构化信贷样本，共 1000 条。
- `german.doc`：字段编码说明。
- 下载脚本：`agent-service/scripts/download_german_credit.py`。
- 原始文件保存目录：`data/raw/german_credit/`。

本项目使用公开数据集和模拟映射验证工程可行性，不代表真实银行生产风控模型。模型输出仅作为审批辅助信号，不能用于自动放贷决策。

## 为什么选择 German Credit

German Credit 是经典公开教学数据集，包含贷款期限、金额、信用历史、就业年限、资产/储蓄信号、年龄和好坏样本标签。它适合做本项目第二轮的结构化风控 baseline，因为它足够小、字段清晰、可离线复现，也不会涉及真实银行客户隐私。

## 字段映射逻辑

原始 German Credit 字段是编码字段，本轮在 `agent-service/scripts/prepare_credit_dataset.py` 中映射为项目可理解的字段：

- `term_months`：由 German Credit `duration` 映射。
- `amount`：由 `credit amount` 映射。
- `age`：使用原始 age。
- `purpose`：将 purpose 编码映射为可读贷款用途。
- `work_years`：根据 employment since 编码粗略映射。
- `overdue_count`：根据 credit history 编码粗略映射。
- `asset_proof_count`：根据 property 和 savings 编码粗略映射。
- `monthly_income`：German Credit 没有真实收入，本项目用贷款金额、期限、分期压力构造模拟月收入。
- `existing_debt`：根据贷款金额、已有授信数量和分期压力构造模拟负债。
- `debt_income_ratio`：使用模拟负债与模拟年收入计算。
- `ground_truth_risk`：原始 good credit 映射为 `LOW`，bad credit 映射为 `HIGH`。

这些映射只用于教学和工程演示，不代表真实银行风控特征工程。

## 特征列表

Logistic Regression baseline 当前使用以下数值特征：

- `age`
- `monthly_income`
- `work_years`
- `existing_debt`
- `overdue_count`
- `asset_proof_count`
- `amount`
- `term_months`
- `debt_income_ratio`

标签字段为 `ground_truth_risk`。

## 模型选择

本轮选择 `LogisticRegression` 作为主模型：

- 训练速度快，适合本地演示。
- 输出概率，方便后续和规则评分融合。
- 可解释性强于复杂黑盒模型，适合面试讲解 baseline。

当前没有接入 RandomForest，也没有接入真实 LLM、RAG、RiskAgent 工作流。

## 训练流程

从仓库根目录或 `agent-service` 目录运行：

```bash
cd agent-service
python scripts/download_german_credit.py
python scripts/prepare_credit_dataset.py
python scripts/train_risk_model.py
pytest tests -q
```

如果网络不可用，请手动下载 `german.data` 和 `german.doc`，放到：

```text
data/raw/german_credit/
```

然后从 `prepare_credit_dataset.py` 继续执行。

## 评估指标

当前本地训练结果保存在 `data/eval/model_metrics.json`：

```json
{
  "accuracy": 0.6,
  "precision": 0.3936,
  "recall": 0.6167,
  "f1": 0.4805,
  "roc_auc": 0.6787,
  "confusion_matrix": [[83, 57], [23, 37]],
  "test_size": 200,
  "train_size": 800,
  "random_seed": 42
}
```

这些指标只能说明 baseline 在公开教学数据和模拟映射上的表现，不能说明真实银行风控能力。

## 生成文件

- `data/raw/german_credit/german.data`
- `data/raw/german_credit/german.doc`
- `data/processed/credit_cases.csv`
- `data/processed/train.csv`
- `data/processed/test.csv`
- `data/eval/model_metrics.json`
- `data/eval/model_eval_cases.jsonl`
- `data/seed/generated_customers_seed.sql`
- `data/seed/generated_loan_applications_seed.sql`
- `agent-service/models/credit_risk_model.joblib`
- `agent-service/models/model_metadata.json`

## RiskModelService

`agent-service/app/services/risk_model_service.py` 提供 `RiskModelService`，可以加载 `credit_risk_model.joblib` 并通过 `predict_risk(features)` 返回：

```json
{
  "model_risk_probability": 0.73,
  "model_risk_label": "HIGH",
  "model_version": "logistic_regression_baseline",
  "features_used": [],
  "explanation": []
}
```

本轮只提供服务类和测试，不把模型接入 `RiskAgent`。

## 模型局限性

- German Credit 是公开教学数据集，不是中国银行真实业务数据。
- 月收入、负债、逾期次数、资产证明数量是从编码字段模拟映射出来的，不是真实客户画像。
- Logistic Regression 是 baseline，不代表最终模型方案。
- 当前模型只输出辅助信号，不能自动审批、自动拒贷或替代人工审批。
- 训练指标不高，适合用于工程链路展示，不适合用于生产风控宣传。

## 为什么不能吹成真实银行风控模型

真实银行风控模型需要合规授权数据、严格特征治理、样本时间窗设计、拒绝推断、稳定性监控、公平性评估、模型审批、灰度验证和贷后表现回流。本项目当前只完成公开数据到工程链路的 baseline，因此简历表达应强调“公开数据 + 模拟映射 + baseline + 审批辅助”，不能表述为“银行级真实风控模型”。

## 下一轮接入 RiskAgent

下一轮可以把 `RiskAgent` 从纯规则评分升级为“规则评分 + ML 模型概率”的组合：

1. 保留当前规则评分，保证可解释和稳定。
2. 调用 `RiskModelService.predict_risk()` 获得模型概率。
3. 将规则分、模型概率、命中原因一起写入 `risk_assessment`。
4. 在 AI 报告中明确区分规则原因和模型信号。
5. 继续由人工审批接口决定最终 `APPROVED`、`REJECTED` 或 `NEED_MORE_INFO`。
