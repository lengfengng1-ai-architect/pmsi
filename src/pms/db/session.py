"""请求级 AsyncSession 依赖：按 contextvar 中的 tenant 取会话。"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from pms.db.tenant import ctx_tenant_id, get_sessionmaker


async def get_session() -> AsyncIterator[AsyncSession]:
    tenant_id = ctx_tenant_id.get()
    if not tenant_id:
        raise RuntimeError("tenant not resolved (middleware missed?)")
    sessionmaker = get_sessionmaker(tenant_id)
    async with sessionmaker() as session:
        yield session
