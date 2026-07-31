"""决策 Pydantic schemas（与 docs/api/paths/decisions.yaml 对齐）。

注：DecisionCreate 增 project_id（spec 暂缺，见 openspec change proposal 的 spec gap）。
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from pms.decisions.models import DecisionOption


class DecisionOptionIn(BaseModel):
    seq: int
    description: str
    schedule_impact: str | None = None
    cost_impact: Decimal | None = None
    scope_impact: str | None = None
    quality_impact: str | None = None
    pros: str | None = None
    cons: str | None = None
    is_recommended: bool = False

    def to_model(self) -> DecisionOption:
        return DecisionOption(**self.model_dump())


class DecisionCreate(BaseModel):
    project_id: UUID
    title: str
    background: str
    options: list[DecisionOptionIn] = Field(min_length=2)  # AC-DM-01：≥2
    decider_user_ref: UUID
    due_at: datetime
    impact_level: Literal["low", "med", "high"]
    impact_evidence_id: UUID | None = None  # TODO Evidence 落地后必填(AC-X02)
    linked_milestone_id: UUID | None = None


class DecisionOptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    seq: int
    description: str
    is_recommended: bool
    is_chosen: bool


class DecisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    status: str
    impact_level: str
    decider_user_ref: UUID
    submitter_user_ref: UUID
    due_at: datetime
    decided_at: datetime | None = None
    version: int
    options: list[DecisionOptionOut]


class DecideRequest(BaseModel):
    chosen_option_seq: int
    rationale: str


class TransitionResponse(BaseModel):
    """状态迁移响应（spec Transitioned：{action, from, to, at, by, version}）。"""

    model_config = ConfigDict(populate_by_name=True)

    action: str
    source: str = Field(serialization_alias="from")
    to: str
    at: datetime
    by: UUID
    version: int
