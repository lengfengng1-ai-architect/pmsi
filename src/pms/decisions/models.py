"""决策聚合 + 选项（docs/15 §4.3）。

注：project_id / impact_evidence_id / linked_milestone_id 为 UUID 引用（无 FK），
待 Project/Evidence/Milestone 模型落地后补外键与存在性校验。
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pms.db.base import Base, TimestampMixin, UUIDPk, VersionMixin


class Decision(Base, UUIDPk, VersionMixin, TimestampMixin):
    __tablename__ = "decision"

    project_id: Mapped[uuid.UUID] = mapped_column()  # ref → Project（待建）
    title: Mapped[str] = mapped_column(String(300))
    background: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    impact_level: Mapped[str] = mapped_column(String(10))  # low/med/high
    impact_evidence_id: Mapped[uuid.UUID] = mapped_column()  # ref → Evidence（待建）
    decider_user_ref: Mapped[uuid.UUID] = mapped_column()
    submitter_user_ref: Mapped[uuid.UUID] = mapped_column()
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    linked_milestone_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    debt_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    options: Mapped[list["DecisionOption"]] = relationship(
        back_populates="decision", cascade="all, delete-orphan"
    )


class DecisionOption(Base, UUIDPk, TimestampMixin):
    __tablename__ = "decision_option"

    decision_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("decision.id"))
    seq: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    schedule_impact: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cost_impact: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    scope_impact: Mapped[str | None] = mapped_column(String(200), nullable=True)
    quality_impact: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pros: Mapped[str | None] = mapped_column(Text, nullable=True)
    cons: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_recommended: Mapped[bool] = mapped_column(default=False)
    is_chosen: Mapped[bool] = mapped_column(default=False)

    decision: Mapped["Decision"] = relationship(back_populates="options")
