# Reassessment Flow Design

## 背景

当前 Demo 中，人工选择 `NEED_MORE_INFO` 后把申请视为终态，已经足够展示“AI 只给建议，最终状态由人工确认”的边界。但真实信贷业务里，补充材料后通常需要重新提交、重新 AI review、重新人工复核，而不是停留在一次性终态。

## 推荐状态流

完整方案：

```text
DRAFT -> SUBMITTED -> AI_REVIEWED -> NEED_MORE_INFO
      -> MATERIAL_UPDATED -> RESUBMITTED -> AI_REVIEWED
      -> APPROVED / REJECTED
```

轻量方案：

```text
NEED_MORE_INFO -> SUBMITTED
```

完整方案的优点是状态语义清晰，能区分“已补件但未重提”和“已重提待 AI review”；缺点是状态数量更多，前后端都要适配。轻量方案改动小，适合 Demo 或早期版本；缺点是审计语义较弱，需要额外日志解释补件和重提动作。

## 数据设计建议

- `material_update_record`：记录每次补件的字段、文件摘要、操作者、时间、备注和关联申请。
- `application_material_snapshot`：保存每次 AI review 使用的材料快照，保证复评可复现。
- `approval_record`：继续只记录人工最终审批动作，不混入 AI 自动决策。
- `audit_log`：记录材料更新、重新提交、重新 AI review、人工审批等关键动作。
- `ai_decision_report`：每次 AI review 新增一条报告，不覆盖旧报告；通过 `workflow_id` 或 review round 区分版本。

## API 建议

```text
POST /api/loan-applications/{id}/materials
POST /api/loan-applications/{id}/resubmit
```

`POST /materials` 用于保存补充材料或材料摘要，写入材料更新记录和审计日志。`POST /resubmit` 用于把已补件申请重新提交到待 AI review 状态，之后必须重新触发 AI review。

## 风险边界

- 补件后必须重新 AI review，不能沿用旧 AI 建议直接人工终审。
- 旧 AI 报告不能覆盖，所有复评报告都要保留。
- 材料更新、重提、复评和人工终审都必须 audit log 留痕。
- AI 仍然不能自动写入 `APPROVED`、`REJECTED` 或 `NEED_MORE_INFO`。
- 补件材料不得包含真实身份证、手机号、银行账号、真实征信报告或真实 API Key。

## 面试话术

可以这样解释：当前 Demo 把 `NEED_MORE_INFO` 做成终态，是为了突出人工审批边界和避免过度扩展；真实业务中会把补件拆成材料更新、重新提交、重新 AI review 和人工复核四步，并保留每一轮材料快照与 AI 报告。这样既能支持复评，又不会让 AI 绕过人工最终审批。
