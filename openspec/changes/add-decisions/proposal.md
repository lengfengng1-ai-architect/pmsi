# Proposal: add-decisions

## Why
决策管理（docs/05）是 MVP 核心护城河（"推"），spec 已就绪（docs/api/paths/decisions.yaml）。本 change 实现第一个垂直切片，验证脚手架 + 流程门。

## What
- Decision / DecisionOption / AuditEvent 模型（docs/15）
- 决策状态机（draft→pending→decided，docs/07 图4 子集）
- 端点：`POST /v1/decisions`、`POST /v1/decisions/{id}/submit`、`POST /v1/decisions/{id}/decide`
- 守卫：唯一决策人（AC-DM-03）、乐观锁（AC-CONCUR-01）、审计同事务、非法迁移→422
- 测试覆盖成功路径 + 守卫失败

## Non-goals（本切片不做，后续 change）
- escalate/fallback/close/withdraw 端点（同模式扩展）
- AC-DM-01a 选项互斥校验、AC-DM-12b due≤里程碑、AC-X02 证据强制（依赖 Evidence/Milestone 模型，后续）
- Alembic 迁移脚本（下一基础设施 change；测试用 create_all）
- RBAC 实装（require_perm 仍为桩）

## Spec gap（须人确认）
`decisions.yaml` 的 `DecisionCreate` 未列 `project_id`，但决策须归属项目——本实现加了 `project_id`。**建议 spec 补该字段**（AI 不擅自定语义，此处标记待定）。
