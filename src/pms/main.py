"""FastAPI 应用工厂：中间件 + 异常处理 + 路由装配。

启动：uv run uvicorn pms.main:app --reload
"""

from fastapi import FastAPI

from pms.api.errors import (
    conflict_handler,
    domain_error_handler,
    generic_handler,
)
from pms.api.routes import router as meta_router
from pms.db.tenant import TenantMiddleware
from pms.shared_kernel.exceptions import ConflictError, DomainError


def create_app() -> FastAPI:
    app = FastAPI(title="PMS", version="0.1.0")

    # 中间件：租户解析（最外层，contextvars 注入）
    app.add_middleware(TenantMiddleware)

    # 异常 → APIError
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(ConflictError, conflict_handler)
    app.add_exception_handler(Exception, generic_handler)

    # 路由
    app.include_router(meta_router)
    # TODO: 业务上下文 router（如 decisions）按 docs/16 逐个挂载

    return app


app = create_app()
