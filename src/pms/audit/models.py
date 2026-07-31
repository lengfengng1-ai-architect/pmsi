"""AuditEvent + 记录助手。append-only：同事务 INSERT，生产靠权限/触发器禁改删。"""

import uuid
from typing import Any

from sqlalchemy import JSON, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from pms.db.base import Base, TimestampMixin, UUIDPk


class AuditEvent(Base, UUIDPk, TimestampMixin):
    __tablename__ = "audit_event"

    actor_user_ref: Mapped[uuid.UUID] = mapped_column()
    action: Mapped[str] = mapped_column(String(100))  # create/submit/decide/...
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[uuid.UUID] = mapped_column()
    before: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    after: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


async def record_audit(
    session: AsyncSession,
    *,
    actor: uuid.UUID,
    action: str,
    entity_type: str,
    entity_id: uuid.UUID,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> None:
    """同事务追加一条审计（随外层 commit 落库）。"""
    session.add(
        AuditEvent(
            actor_user_ref=actor,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before=before,
            after=after,
        )
    )
