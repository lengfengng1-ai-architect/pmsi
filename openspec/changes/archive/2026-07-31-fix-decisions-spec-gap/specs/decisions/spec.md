# decisions spec delta (fix-decisions-spec-gap)

> 清 add-decisions 遗留的 spec gap：`project_id` 补进契约，`impact_evidence_id` 收紧回必填（AC-X02）。

## MODIFIED Requirements

### Requirement: 决策卡创建

决策卡 SHALL 带归属项目、标题、背景、≥2 选项、唯一决策人、截止、影响等级，且影响等级 SHALL 挂证据（AC-X02 首次定级即须证据）。

#### Scenario: 合法创建

- **WHEN** 提交含 `project_id`、`impact_evidence_id` 且 ≥2 选项的决策卡
- **THEN** 返回 201 且 `status=draft`
- **AND** 响应 SHALL 带 `ETag=version`

#### Scenario: 选项不足

- **WHEN** `options` 少于 2 项
- **THEN** 返回 422（schema `minItems`）

#### Scenario: 缺归属项目

- **WHEN** 创建请求未带 `project_id`
- **THEN** 返回 422

#### Scenario: 缺影响证据

- **WHEN** 创建请求未带 `impact_evidence_id`
- **THEN** 返回 422（AC-X02）
