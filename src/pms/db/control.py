"""控制库模型（单一，跨租户）：租户/用户/成员。设计见 docs/15 §五。"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from pms.db.base import Base, TimestampMixin, UUIDPk


class Tenant(Base, UUIDPk, TimestampMixin):
    __tablename__ = "tenant"

    name: Mapped[str] = mapped_column(String(200))
    subdomain: Mapped[str] = mapped_column(String(100), unique=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    # secret 引用，非明文 DSN（运行时从 secret manager 解析）
    db_dsn_ref: Mapped[str] = mapped_column(Text)


class User(Base, UUIDPk, TimestampMixin):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(String(320), unique=True)
    display_name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="active")
