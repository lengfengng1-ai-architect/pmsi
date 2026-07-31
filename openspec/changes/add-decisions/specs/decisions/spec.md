# decisions spec delta (add-decisions)

> 示范：AC（docs/06 AC-DM-*）→ Spec Scenario。完整契约见 docs/api/paths/decisions.yaml。

## ADDED Requirements

### Requirement: 决策卡创建
决策卡须带标题、背景、≥2 选项、唯一决策人、截止、影响等级。
- **Scenario: 合法创建** — WHEN 提交 ≥2 选项的决策卡 THEN 返回 201 且 status=draft SHALL ETag=version
- **Scenario: 选项不足** — WHEN options < 2 THEN 返回 422（schema minItems）

### Requirement: 决策人唯一性
- **Scenario: 非决策人拍板** — WHEN actor ≠ decider 调用 decide THEN 返回 422 not_decider（AC-DM-03）

### Requirement: 状态迁移合法性
- **Scenario: 合法 decide** — GIVEN 已 submit(pending) WHEN decider decide THEN status=decided，记 decided_at + chosen option
- **Scenario: 非法迁移** — WHEN 从 draft 直接 decide THEN 返回 422 illegal_transition

### Requirement: 乐观锁
- **Scenario: 版本冲突** — WHEN If-Match version 与当前不符 THEN 返回 409 conflict（AC-CONCUR-01）

### Requirement: 审计同事务
- **Scenario: 迁移留痕** — WHEN create/submit/decide THEN 同事务 INSERT audit_event（before/after）
