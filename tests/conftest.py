"""pytest fixture：async ASGI client + 隔离 DB（sqlite in-memory，不连真实外部服务）。"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import pms.audit.models  # noqa: F401  注册到 Base.metadata
import pms.db.control  # noqa: F401
import pms.decisions.models  # noqa: F401
from pms.db.base import Base
from pms.db.session import get_session
from pms.main import create_app


@pytest.fixture
async def client():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    app = create_app()

    async def _override_session():
        async with sessionmaker() as session:
            yield session

    app.dependency_overrides[get_session] = _override_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()
