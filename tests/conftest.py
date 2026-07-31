"""pytest 公共 fixture：async ASGI client（不连真实外部服务）。"""

import pytest
from httpx import ASGITransport, AsyncClient

from pms.main import create_app


@pytest.fixture
async def client():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
