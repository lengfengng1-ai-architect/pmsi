"""健康检查端点测试（命名 test_{fn}__{scenario}__{outcome}，AAA 结构）。"""


async def test_health__get__returns_ok(client):
    # Act
    resp = await client.get("/health")
    # Assert
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


async def test_tenant_middleware__public_path__no_tenant_required(client):
    # Arrange: 故意不传 X-Tenant；/ping 在 PUBLIC_PATHS，应不报 tenant 错
    # Act
    resp = await client.get("/ping")
    # Assert
    assert resp.status_code == 200
    assert resp.json() == {"pong": True}
