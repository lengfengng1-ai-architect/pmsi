"""领域异常 → 统一 APIError 响应（docs/16 §十 / docs/api/_template.yaml）。"""

from fastapi import Request
from fastapi.responses import JSONResponse

from pms.shared_kernel.exceptions import ConflictError, DomainError, NotFoundError


def _error(code: str, message: str, details: dict) -> dict:
    return {"error": {"code": code, "message": message, "details": details}}


async def domain_error_handler(_req: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=422, content=_error(exc.code, exc.message, exc.details))


async def not_found_handler(_req: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content=_error(exc.code, exc.message, exc.details))


async def conflict_handler(_req: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content=_error(exc.code, exc.message, exc.details))


async def generic_handler(_req: Request, _exc: Exception) -> JSONResponse:
    # ponytail: 不向客户端泄露内部堆栈
    return JSONResponse(status_code=500, content=_error("internal_error", "internal error", {}))
