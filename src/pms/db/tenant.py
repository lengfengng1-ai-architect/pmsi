"""一租户一库引擎路由（docs/14 §二 / docs/16 依赖链）。

中间件解析 tenant_id → contextvars；get_session 依赖据此取/建该租户的
AsyncEngine + AsyncSession。控制库走默认 session（另接）。
每请求重置 contextvar，禁跨租户会话复用（docs/18 隔离）。
"""

import contextvars

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from pms.config import settings

# ponytail: 单进程内的引擎注册表；规模大后按 LRU 回收 + 按租户分库集群分组
_engine_registry: dict[str, AsyncEngine] = {}
_sessionmakers: dict[str, async_sessionmaker[AsyncSession]] = {}

# 请求级租户上下文（中间件 set，依赖/仓储 read）
ctx_tenant_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "tenant_id", default=None
)

# 无需租户解析的路径（健康检查等）
PUBLIC_PATHS = frozenset({"/", "/health", "/ping", "/readiness"})


def _resolve_dsn(tenant_id: str) -> str:
    """租户→库 DSN。MVP：控制库 tenant.db_dsn_ref 查 secret manager；此处先回落控制库 DSN。"""
    # TODO: 从控制库 tenant 表查 db_dsn_ref 并解析（docs/15 §五 tenant 表）
    return settings.control_db_dsn


def get_engine(tenant_id: str) -> AsyncEngine:
    if tenant_id not in _engine_registry:
        _engine_registry[tenant_id] = create_async_engine(
            _resolve_dsn(tenant_id), pool_pre_ping=True
        )
    return _engine_registry[tenant_id]


def get_sessionmaker(tenant_id: str) -> async_sessionmaker[AsyncSession]:
    if tenant_id not in _sessionmakers:
        _sessionmakers[tenant_id] = async_sessionmaker(
            get_engine(tenant_id), expire_on_commit=False
        )
    return _sessionmakers[tenant_id]


class TenantMiddleware:
    """纯 ASGI 中间件：解析 tenant 入 contextvar（业务库据此路由）。

    开发期：X-Tenant 头；生产：子域或 JWT claim（docs/16）。
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http" or scope.get("path") in PUBLIC_PATHS:
            return await self.app(scope, receive, send)
        headers = {k.decode(): v.decode() for k, v in scope.get("headers", [])}
        tenant_id = headers.get(settings.tenant_header) or "default"
        token = ctx_tenant_id.set(tenant_id)
        try:
            await self.app(scope, receive, send)
        finally:
            ctx_tenant_id.reset(token)
