"""决策路由（docs/16 §5.2）。REST create + 动作式 submit/decide。"""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from pms.api.deps import CurrentUser, IfMatch
from pms.db.session import get_session
from pms.decisions import service
from pms.decisions.schemas import (
    DecideRequest,
    DecisionCreate,
    DecisionOut,
    TransitionResponse,
)

router = APIRouter(prefix="/v1/decisions", tags=["decisions"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("", response_model=DecisionOut, status_code=status.HTTP_201_CREATED)
async def create_decision(
    payload: DecisionCreate, response: Response, session: SessionDep, user: CurrentUser
):
    decision = await service.create_decision(session, payload, user)
    response.headers["ETag"] = str(decision.version)
    return decision


@router.post("/{decision_id}/submit", response_model=TransitionResponse)
async def submit_decision(
    decision_id: UUID, response: Response, session: SessionDep, user: CurrentUser, if_match: IfMatch
):
    decision, prev = await service.submit_decision(session, decision_id, user, if_match)
    response.headers["ETag"] = str(decision.version)
    return TransitionResponse(
        action="submit",
        source=prev,
        to=decision.status,
        at=datetime.now(UTC),
        by=user,
        version=decision.version,
    )


@router.post("/{decision_id}/decide", response_model=TransitionResponse)
async def decide_decision(
    decision_id: UUID,
    payload: DecideRequest,
    response: Response,
    session: SessionDep,
    user: CurrentUser,
    if_match: IfMatch,
):
    decision, prev = await service.decide_decision(session, decision_id, payload, user, if_match)
    response.headers["ETag"] = str(decision.version)
    return TransitionResponse(
        action="decide",
        source=prev,
        to=decision.status,
        at=decision.decided_at or datetime.now(UTC),
        by=user,
        version=decision.version,
    )
