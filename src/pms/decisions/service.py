"""决策服务层（不感知 HTTP，docs/16 实现顺序）。守卫 + 状态机 + 审计同事务 + 乐观锁。"""

import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from pms.audit.models import record_audit
from pms.decisions.models import Decision
from pms.decisions.schemas import DecideRequest, DecisionCreate
from pms.shared_kernel.exceptions import ConflictError, NotDeciderError, NotFoundError
from pms.shared_kernel.state_machine import build_machine, safe_trigger

# docs/07 图4 子集（本切片：draft→pending→decided）
_STATES = ["draft", "pending", "escalating", "decided", "executed", "closed", "withdrawn"]
_TRANSITIONS = [
    {"trigger": "submit", "source": "draft", "dest": "pending"},
    {"trigger": "decide", "source": ["pending", "escalating"], "dest": "decided"},
]


def _attach(d: Decision) -> None:
    build_machine(d, states=_STATES, transitions=_TRANSITIONS, initial=d.status)


def _check_version(d: Decision, expected: int) -> None:
    # ponytail: 真并发用 UPDATE...WHERE version=? 校验；此处 load 后比对，生产改 WHERE 子句
    if d.version != expected:
        raise ConflictError("version conflict", {"expected": d.version})


async def _load(session: AsyncSession, decision_id: uuid.UUID) -> Decision:
    d = await session.get(Decision, decision_id, options=[selectinload(Decision.options)])
    if d is None:
        raise NotFoundError("decision not found")
    return d


async def create_decision(
    session: AsyncSession, payload: DecisionCreate, actor: uuid.UUID
) -> Decision:
    decision = Decision(
        project_id=payload.project_id,
        title=payload.title,
        background=payload.background,
        status="draft",
        impact_level=payload.impact_level,
        impact_evidence_id=payload.impact_evidence_id,
        decider_user_ref=payload.decider_user_ref,
        submitter_user_ref=actor,
        due_at=payload.due_at,
        linked_milestone_id=payload.linked_milestone_id,
        options=[o.to_model() for o in payload.options],
    )
    session.add(decision)
    await session.flush()  # 拿 id
    await record_audit(
        session,
        actor=actor,
        action="create",
        entity_type="decision",
        entity_id=decision.id,
        after={"status": "draft"},
    )
    await session.commit()
    return decision


async def submit_decision(
    session: AsyncSession, decision_id: uuid.UUID, actor: uuid.UUID, expected_version: int
) -> tuple[Decision, str]:
    d = await _load(session, decision_id)
    _check_version(d, expected_version)
    prev = d.status
    _attach(d)
    safe_trigger(d, "submit")  # draft→pending
    d.version += 1
    await record_audit(
        session,
        actor=actor,
        action="submit",
        entity_type="decision",
        entity_id=d.id,
        before={"status": prev},
        after={"status": d.status},
    )
    await session.commit()
    return d, prev


async def decide_decision(
    session: AsyncSession,
    decision_id: uuid.UUID,
    payload: DecideRequest,
    actor: uuid.UUID,
    expected_version: int,
) -> tuple[Decision, str]:
    d = await _load(session, decision_id)
    _check_version(d, expected_version)
    if d.decider_user_ref != actor:
        raise NotDeciderError("only the designated decider may decide")  # AC-DM-03
    prev = d.status
    _attach(d)
    safe_trigger(d, "decide")  # pending/escalating→decided；draft 等非法→IllegalTransitionError
    d.decided_at = datetime.now(UTC)
    for option in d.options:
        option.is_chosen = option.seq == payload.chosen_option_seq
    d.version += 1
    await record_audit(
        session,
        actor=actor,
        action="decide",
        entity_type="decision",
        entity_id=d.id,
        before={"status": prev},
        after={"status": d.status, "chosen": payload.chosen_option_seq},
    )
    await session.commit()
    return d, prev
