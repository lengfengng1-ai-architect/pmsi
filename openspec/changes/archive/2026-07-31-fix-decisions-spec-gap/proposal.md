# Proposal: fix-decisions-spec-gap

## Why

`docs/api/paths/decisions.yaml` 的 `DecisionCreate` 与 `docs/15 §4.3` 数据模型不一致，导致 add-decisions 切片实现时被迫偏离 spec：

1. **`project_id` 漏抄**：docs/15:162 明确定义 `project_id | uuid FK`，但 yaml 的 `DecisionCreate` 既不在 required 也不在 properties。实现只能自行加上（`schemas.py:32`），并在注释里挂账。
2. **`impact_evidence_id` 被放宽**：yaml 与 docs/15 都是 required（AC-X02 首次定级即须证据），但实现写成 `UUID | None = None`，理由是 Evidence 模型未落地。

结果是 spec 与代码两处不一致，违反 CLAUDE.md §3「字段名/类型/校验与 OpenAPI 完全一致」。此账挂在 add-decisions 的 proposal 里已归档，再不清理会被遗忘。

## What Changes

- `decisions.yaml` 的 `DecisionCreate` 补 `project_id`（required，`format: uuid`），并补进 `Decision` 响应 schema
- `schemas.py` 的 `impact_evidence_id` 由 `UUID | None = None` **收紧为必填 `UUID`**（**BREAKING**：现有请求不带该字段将返回 422）
- `models.py` 的 `Decision.impact_evidence_id` 由 nullable 改为 NOT NULL
- 清理 `schemas.py` / `models.py` 中标记 spec gap 的挂账注释
- 测试 fixture 补 `impact_evidence_id`，并加一例「缺证据 → 422」

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `decisions`: 「决策卡创建」requirement 的字段约束收紧——`project_id` 与 `impact_evidence_id` 均为必填

## Impact

**代码**（blast radius 经 codegraph 确认）：
- `docs/api/paths/decisions.yaml` — `DecisionCreate` + `Decision` schema
- `src/pms/decisions/schemas.py` — `DecisionCreate.impact_evidence_id`
- `src/pms/decisions/models.py` — `Decision.impact_evidence_id` 列可空性
- `tests/test_decisions.py` — payload fixture + 新增缺证据用例
- `service.py` 无需改动（已透传 `payload.impact_evidence_id`）

**API**：`POST /v1/decisions` 请求体新增两个必填字段约束。MVP 未上线、无外部调用方，不需要兼容期。

**依赖**：`impact_evidence_id` 仍为无 FK 的 UUID 引用（Evidence 模型未建）。本 change 只保证「必须提供」，不校验「引用存在」——后者留给 evidence 切片。
