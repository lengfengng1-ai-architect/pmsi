# decisions

## Purpose

决策卡（Decision）能力：记录待拍板事项、候选选项与唯一决策人，通过状态机（draft → pending → decided）驱动拍板闭环，并保证禁自审、乐观锁与审计留痕。

权威验收标准见 `docs/06`（AC-DM-*、AC-CONCUR-01）；完整 HTTP 契约见 `docs/api/paths/decisions.yaml`。

## Requirements

### Requirement: 决策卡创建

决策卡 SHALL 带标题、背景、≥2 选项、唯一决策人、截止、影响等级。

#### Scenario: 合法创建

- **WHEN** 提交 ≥2 选项的决策卡
- **THEN** 返回 201 且 `status=draft`
- **AND** 响应 SHALL 带 `ETag=version`

#### Scenario: 选项不足

- **WHEN** `options` 少于 2 项
- **THEN** 返回 422（schema `minItems`）

### Requirement: 决策人唯一性

决策卡 SHALL 有且仅有一名决策人；非决策人 SHALL NOT 拍板（AC-DM-03）。

#### Scenario: 非决策人拍板

- **WHEN** `actor ≠ decider` 调用 decide
- **THEN** 返回 422 `not_decider`

### Requirement: 状态迁移合法性

决策卡状态迁移 SHALL 经状态机守卫，非法迁移 SHALL 由领域层拒绝。

#### Scenario: 合法 decide

- **GIVEN** 决策卡已 submit（`status=pending`）
- **WHEN** decider 调用 decide
- **THEN** `status=decided`
- **AND** 记录 `decided_at` 与选中的 option

#### Scenario: 非法迁移

- **WHEN** 从 `draft` 直接调用 decide
- **THEN** 返回 422 `illegal_transition`

### Requirement: 乐观锁

状态变更 SHALL 携带 `If-Match`，与聚合当前 `version` 不符时 SHALL 拒绝（AC-CONCUR-01）。

#### Scenario: 版本冲突

- **WHEN** `If-Match` 的 version 与当前 version 不符
- **THEN** 返回 409 `conflict`

### Requirement: 审计同事务

状态迁移 SHALL 与审计写入处于同一数据库事务，`audit_event` SHALL append-only。

#### Scenario: 迁移留痕

- **WHEN** 执行 create / submit / decide
- **THEN** 同事务 INSERT `audit_event`
- **AND** 记录 before / after 状态
