"""SQLAlchemy 2 声明基类 + 聚合公用 mixin。设计见 docs/15 §一。"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有模型基类。控制库与租户库共用。"""


class UUIDPk:
    """UUID 主键（TODO: 升 UUID v7 时间有序，索引友好）。"""

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)


class VersionMixin:
    """乐观锁 version（AC-CONCUR-01）：状态迁移 UPDATE WHERE version=?。"""

    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
