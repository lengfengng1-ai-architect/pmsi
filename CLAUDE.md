# 项目管理系统（PMS）— AI 开发约束

本项目用 AI 编码助手开发。以下规则 **AI 必须遵守，每条强制，不可跳过或协商**。
设计依据见 `docs/01–18`（业务设计 + 技术设计）。本文件统辖所有流程与规范。

## 1. 核心开发模式

**人写 Spec → AI 填充实现 → 人 Review。**

| 角色 | 负责 |
|---|---|
| **人** | 定义 API 契约与字段语义、业务规则（docs/05/06 的 AC）、架构决策、安全审查、最终验收 |
| **AI** | 按 OpenAPI spec 生成路由/Pydantic 模型/迁移、实现 CRUD 与数据转换、写状态机迁移与守卫、写测试、写文档 |

**技术栈（人固定，AI 不得擅自引入/替换）**：FastAPI + uv + SQLAlchemy 2 异步(asyncpg) + Alembic + Pydantic v2 + Celery + Redis(beat) + transitions + PostgreSQL（一租户一库）+ React/Vite/TS。详见 docs/14。

**代码放置**：按 docs/14 §三 的限界上下文子包放（`src/<product>/{tenancy,projects,wbs,decisions,risks,changes,health,retro,automation,notifications,audit,evidence,integrations,shared_kernel}`），每子包四层（domain/application/infra/interface）。**不新建顶层目录**。

## 2. 接到新需求/改动后的强制入口流程（Step 0–9，流程门）

> 普通查询/答疑可跳过。**新增功能 / 新 capability / 修改现有行为 / 架构决策 / 跨上下文改动** 必须走完整 0–9。
> 依赖工具链：**OpenSpec CLI + opsx:* 技能 + codegraph + Superpowers（brainstorming/grilling）**——这几样是流程门的承重墙，不可绕过。

| Step | 做什么 | 工具/产物 |
|---|---|---|
| 0 | 回复开头声明「已检查流程技能、判断哪些适用、将调用哪个」 | 触发判断 |
| 1 | **brainstorming**：探索意图与设计，输出 design 草稿 | Superpowers · 未调用即设计/编码=违规 |
| 2 | **grilling**（可选）：拷问已有计划 | Superpowers · 模糊→1，具体→2 |
| 3 | **/opsx:explore**：澄清、消除歧义、细化方案（不写应用代码） | OpenSpec/opsx |
| 4 | **范围审查 YAGNI 三问**：必须建？能用现有能力？能一行/一个配置解决？ | — |
| 5 | **查 codegraph**：改前查符号/调用链/blast radius，避免重复/冲突/改坏调用方 | `codegraph explore` 或 MCP |
| 6 | **读能力边界**：确认在 `superpowers.yaml` 的 `in_scope`；`out_scope` 或不在两栏→提示不做 | superpowers.yaml |
| 7 | **确认 Spec 已存在**：有对应 OpenAPI YAML→按 spec 实现；没有→**不编码**，提示先写 spec | docs/api/paths/*.yaml |
| 8 | **变更流程**：`/opsx:propose`→`apply`→`sync`→`archive`；关键语义/规则/架构等人确认才写码 | OpenSpec/opsx |
| 9 | **编码前强制勾选**：图谱✓ 能力范围✓ Spec/YAML✓ 活跃 change✓，缺一不码（显式列出） | — |

**例外**：用户明确要跳过某步时，AI 须先提醒风险、要求用户明确说「确认跳过 [步骤名]」才执行；相关 skill 不可用时**暂停报告**，不得未确认就继续。

## 3. Spec 规则（契约先于实现）

- **无 spec 不编码**：端点须先有 `docs/api/paths/<capability>.yaml`（OpenAPI 3.1）。
- 字段名/类型/校验与 OpenAPI **完全一致**；`operationId = {resource}_{action}`，对应处理函数名。
- 动作式状态迁移端点 `POST /v1/{resource}/{id}/{action}`（docs/16）。
- 每字段有 description（中文）；枚举值英文、注释工作语言；标识符/变量英文。
- 每端点覆盖 200/400/422/500；错误统一用 `_template.yaml` 的 `APIError`。
- docs/06 的 AC → spec 的 Scenario（WHEN/THEN/SHALL）；每个 spec 对应一个 `superpowers.yaml` 的 in_scope id。

## 4. 能力边界规则

**数据引用最高优先级**：seed/fixture/示例数据中的实体名称（租户/项目/人名）须用真实命名，**LLM 禁止编造**；数值可虚构但须内部一致、跨表 ID 可关联。
> 注意：我们 MVP 数据源是**真实 PostgreSQL**，不是 mock——「mock」在本项目=测试 fixture + 种子数据（默认工作日历/行业模板/示范项目），不是 MVP 运行时数据源。

| LLM 可生成 | LLM 禁止生成 |
|---|---|
| 按 spec 的 CRUD/路由/Pydantic 模型/Alembic 迁移骨架/状态机迁移/测试/文档 | 业务规则与字段语义（docs/05/06 人定） |
| 按现有 codegraph 符号续写（命名一致） | 架构决策、安全阈值、合规规则 |
| 基于 spec/数据的推理实现 | 真实租户/用户数据、编造 seed 命名 |

**遇冲突**（用户要 AI 做禁区）：不默从，指出撞了哪条，给「改边界（人放行 superpowers.yaml）」或「走固定规则/seed」两条路。

## 5. PMS 领域硬约束（通用流程之外的本项目专项）

这些是 docs/05/06/11/15/16 的核心守卫，实现时**必须落地**，Code Review 重点查：

- **状态机**：用 `transitions`，非法迁移→抛领域错误→API `422 illegal_transition`（docs/07 六张状态机）。
- **禁自审**：确认闭环/拍板时 `actor != submitter`（单人项目走 AC-SOLO-01 抽样）。
- **数值证据化（AC-X02）**：风险/影响等级、完成% 等标量（含首次定级）须挂 Evidence + 独立复核，否则服务层拒绝。
- **可追踪对象（AC-X01）**：提交方案/确认闭环/解除告警须产出带 owner+deadline 的行动项，禁纯文本；交付物须过验收 checklist（AC-X01a）。
- **乐观锁**：状态变更聚合 `version` 字段，`If-Match` 头，冲突→`409`（AC-CONCUR-01）。
- **审计同事务**：状态迁移/权限敏感动作在同一 DB 事务内 INSERT `audit_event`，append-only（revoke UPDATE/DELETE + 触发器）。
- **基线不洗白（AC-BASE-02）**：CPI/SPI 对原始基线冻结 PV 累计，重建只喂前瞻 EAC。
- **租户路由**：中间件解析 tenant→引擎注册表→contextvars 注入会话；**每请求重置，禁跨租户会话复用**。
- **范围过滤**：`ScopeFilter` 依赖强制注入（项目成员/对象责任/组合/状态 4 维）；Admin 短路但仍审计。

## 6. 代码图谱规则

- 每次编码前 `codegraph explore` 查符号/调用链/blast radius；查到已有功能直接引用，不重复实现。
- 改签名前同步所有调用方；大型重构后更新 `.codegraph/` 索引（PR/CI 提醒）。

## 7. 代码生成 / 测试 / Seed / Git 规范

- **测试**：pytest + httpx(async)，覆盖率 **≥80%**；命名 `test_{fn}__{scenario}__{outcome}`（双下划线）；AAA 结构（// Arrange/Act/Assert）；端点强制 200/400/422；**禁连真实外部服务**（conftest 提供 async client +隔离库 fixture）。
- **状态机/守卫必测**：合法迁移 + 非法迁移（422）+ 禁自审 + 缺证据 + 乐观锁冲突，各至少一例。
- **Seed/fixture**：`{data, meta}` 结构，字段 snake_case 与 schema 一致，跨表 ID 可关联，命名真实。
- **Git**：`main`(发布) ← `develop`(集成) ← `feat/*/fix*/chore*`(完成即删)；**AI 不得自动切/建分支，必须问用户确认**；commit `<type>: <描述>`（feat/fix/refactor/test/docs/chore/perf/ci）；提交前：测试过、覆盖率达标、有对应 spec YAML、无硬编码凭据、seed 无编造命名、lint 过。
- **非平凡逻辑留一个可运行最小检查**（assert demo 或小测试）；信任边界输入校验/防数据丢失/安全这些硬骨头不图省事。不引入未请求抽象；删除优于添加。

## 8. 违规清单（Code Review 打回）

- 未走 Step 0–9（未 brainstorming/explore/查图谱/读边界/无 spec 编码/无活跃 change/未勾选）
- 字段/类型与 spec 不一致；编造 spec/mock 之外的数据
- 重复实现已有功能；生成 out_scope 功能或无 spec 对应的端点
- 硬编码凭据/配置；自动切/建分支
- 状态机非法迁移未拦、缺禁自审/证据守卫、审计未同事务、跨租户会话复用
- 无测试提交、覆盖率不达标、函数体内 import、字符串拼 prompt（P3 才涉及）

## 9. 设计文档索引

业务：`docs/01` 定位 · `02` 模块 · `03` 对标 · `04` 健康分 · `05` 决策 · `06` 验收(权威AC) · `07` 架构图 · `08` MVP 路线 · `09` 反检验 · `10` PRD · `11` 权责 · `13` 现实工程。
技术：`docs/14` 架构 · `15` 数据模型 · `16` API · `17` 部署运维 · `18` 安全合规。

## 10. Agent 编排（仅 P3 AI 副驾启用，MVP 不涉及）

MVP 不含 LLM agent 编排。`docs/development-workflow-guide.md` 的 §7.7 + 附录 C.6–C.8（LangGraph/registry/build_chat_model/SSE）**留待 P3 AI 副驾时再启用**，当前跳过。
