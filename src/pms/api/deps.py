"""FastAPI 依赖链（docs/16 §二/§三）。

MVP 脚手架：tenant 解析（中间件已设 contextvar）+ CurrentUser（开发期 X-User 头）
真实可用；RequirePerm / ScopeFilter 为 TODO 桩（首个 feature 接 RBAC×范围，docs/11）。
"""

import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from pms.db.tenant import ctx_tenant_id


def current_tenant() -> str:
    """读中间件已解析的 tenant_id。"""
    tenant_id = ctx_tenant_id.get()
    if not tenant_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="tenant not resolved")
    return tenant_id


async def get_current_user(
    x_user: Annotated[str | None, Header(alias="X-User")] = None,
) -> uuid.UUID:
    """开发期：X-User 头 = 用户 UUID。生产：JWT/SSO（docs/18）。"""
    if not x_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="unauthenticated")
    try:
        return uuid.UUID(x_user)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid user") from None


# 类型别名（Annotated，ruff-clean，路由函数直接用）
CurrentUser = Annotated[uuid.UUID, Depends(get_current_user)]


def require_perm(action: str):
    """功能权限依赖工厂（docs/11 矩阵 → action）。

    TODO: 查当前用户在当前 tenant 的角色是否持有该 action；
          Admin 短路放行（仍审计 AC-ADMIN-01）。
    """

    async def _dep(user: CurrentUser) -> uuid.UUID:
        return user  # 桩：通过；首个 feature 实装 RBAC

    _dep.__name__ = f"require_perm_{action}"
    return _dep


async def if_match(if_match: Annotated[str, Header()]) -> int:
    """乐观锁 version（AC-CONCUR-01）：状态迁移端点必传，冲突→409。"""
    try:
        return int(if_match)
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="invalid If-Match") from None


IfMatch = Annotated[int, Depends(if_match)]
