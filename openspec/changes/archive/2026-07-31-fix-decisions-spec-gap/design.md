# Design: fix-decisions-spec-gap

## Context

add-decisions 切片实现时发现 `decisions.yaml` 与 `docs/15 §4.3` 两处不一致，当时选择「实现里先加 + 注释挂账」，导致 spec 与代码分叉。本 change 清账。

当前状态：
- `docs/15:162` 定义 `project_id | uuid FK`，`docs/15:166` 定义 `impact_evidence_id | uuid FK→evidence`（均无 nullable 标记）
- `decisions.yaml:203` 的 required 列表含 `impact_evidence_id`，不含 `project_id`；properties 同样缺 `project_id`
- `schemas.py:32` 有 `project_id: UUID`（必填）；`schemas.py:39` 的 `impact_evidence_id` 为可选
- 无 Alembic 迁移（add-decisions 的 Non-goals 已声明），测试用 `create_all`

约束：字段语义属人的决策范围（CLAUDE.md §4），本 change 的两个取向已经用户确认——`project_id` 写进 `DecisionCreate` body（非嵌套路径），`impact_evidence_id` 保持 required 并让实现收紧。

## Goals / Non-Goals

**Goals:**
- `decisions.yaml`、`docs/15`、实现三者在 `project_id` / `impact_evidence_id` 上完全一致
- 缺证据的创建请求被拒（AC-X02 首次定级即须证据）
- 清除代码里标记 spec gap 的挂账注释

**Non-Goals:**
- 不建 Evidence 模型，不加 FK 约束，不校验 evidence 引用是否真实存在（留给 evidence 切片）
- 不做 Alembic 迁移（无迁移基线，下一个基础设施 change 统一处理）
- 不动 `linked_milestone_id` / `is_solo` / `debt_started_at` 等本切片未实现的字段
- 不改 `POST /v1/decisions` 的路径形态

## Decisions

**D1：`project_id` 放 body，不改嵌套路径。**
备选是 `POST /v1/projects/{project_id}/decisions`，REST 层级更正。否决理由：docs/16 现有端点全是 `/v1/{resource}` 平铺风格，改嵌套会让 decisions 成为孤例，且要动路由/实现/测试三处。放 body 与现有实现一致，改动面最小。

**D2：`impact_evidence_id` 收紧为必填，不等 Evidence 模型。**
备选是把 yaml 改成可选、等 Evidence 落地再收紧。否决理由：AC-X02 是硬约束（CLAUDE.md §5「数值证据化」），放宽 spec 等于把守卫推迟到一个没有排期的切片，而「先放宽再收紧」的收紧动作历史上就是会被忘掉——本 change 本身就是证据。字段类型上先要求提供 UUID，语义校验（引用是否存在、是否已复核）留给 evidence 切片，是可以分层的。

**D3：NOT NULL 直接改列定义，不写迁移。**
项目尚无 Alembic 基线，测试走 `create_all`，改 `mapped_column(nullable=False)` 即可生效。首个迁移生成时会把当前模型作为基线一次性纳入。若未来已有生产数据再收紧，则需要 backfill + `ALTER COLUMN SET NOT NULL` 两步，本 change 不涉及。

**D4：Pydantic 层与 DB 层同时收紧。**
只改 Pydantic 会让 DB 仍可写入 NULL（其他入口绕过 schema）；只改 DB 会让错误变成 500 而非 422。两层都改，422 由 Pydantic 给出，DB 约束兜底。

## Risks / Trade-offs

- **BREAKING：现有不带 `impact_evidence_id` 的请求将 422** → MVP 未上线、无外部调用方，无需兼容期。测试 fixture 同步更新即可。
- **`impact_evidence_id` 必填但不校验存在性** → 调用方可传任意 UUID 蒙混过关。这是 D2 分层的已知代价；evidence 切片补 FK + 存在性校验时会关闭这个口子。记在 Non-Goals，不用注释挂账（挂账正是本 change 要消除的模式）。
- **无迁移** → 若在 Alembic 基线建立前有人手工建过库，改列后需重建。当前只有测试库和本地开发库，影响可忽略。
