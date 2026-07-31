# Tasks: fix-decisions-spec-gap

按 docs/16 固定顺序：spec → 模型 → schemas → 测试。service 层无需改动（已透传）。

## 1. Spec（契约先行）

- [x] 1.1 `decisions.yaml` 的 `DecisionCreate`：properties 补 `project_id`（uuid，description 中文），required 列表补 `project_id`
- [x] 1.2 `decisions.yaml` 的 `Decision` 响应 schema：properties 补 `project_id`

## 2. 实现收紧

- [x] 2.1 `models.py`：`Decision.impact_evidence_id` 由 nullable 改为 NOT NULL（D3/D4）
- [x] 2.2 `schemas.py`：`DecisionCreate.impact_evidence_id` 由 `UUID | None = None` 改为必填 `UUID`
- [x] 2.3 清理挂账注释：`schemas.py` 模块 docstring 的 spec gap 说明、`impact_evidence_id` 的 TODO、`models.py` docstring 中 evidence 相关表述

## 3. 测试

- [x] 3.1 `test_decisions.py` payload fixture 补 `impact_evidence_id`
- [x] 3.2 新增 `test_create_decision__missing_evidence__returns_422`
- [x] 3.3 新增 `test_create_decision__missing_project_id__returns_422`

## 4. 验证

- [x] 4.1 `ruff check .` + `pytest` 全绿
- [x] 4.2 `openspec validate --all` 全绿
