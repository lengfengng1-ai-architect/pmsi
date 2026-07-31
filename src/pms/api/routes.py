"""公共路由（health/ping/readiness），无需租户/认证。"""

from fastapi import APIRouter

router = APIRouter(tags=["meta"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/ping")
async def ping() -> dict:
    return {"pong": True}


@router.get("/readiness")
async def readiness() -> dict:
    # TODO: 检查控制库/Redis 连通
    return {"ready": True}
