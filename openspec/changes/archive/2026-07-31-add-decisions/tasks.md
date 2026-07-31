# Tasks: add-decisions

实现顺序（docs/16 固定顺序：spec→模型→service→router→seed/fixture→测试）。

- [x] 1. 模型：`Decision`、`DecisionOption`（docs/15）、`AuditEvent` + `record_audit`
- [x] 2. 领域异常：`NotFoundError`(→404)、`NotDeciderError`(→422)
- [x] 3. Pydantic schemas（与 decisions.yaml 一致 + project_id）
- [x] 4. 状态机配置（STATES/TRANSITIONS）+ service：create/submit/decide（守卫+审计+乐观锁）
- [x] 5. router：POST `/`、`/{id}/submit`、`/{id}/decide`（Depends: session/CurrentUser/IfMatch）
- [x] 6. 装配 main + 错误处理（NotFoundError→404）
- [x] 7. conftest：sqlite in-memory + get_session override
- [x] 8. 测试：create 201 / submit 200 / decide 200 / 非决策人 422 / 版本冲突 409 / 非法迁移 422
- [x] 9. ruff + pytest 通过
