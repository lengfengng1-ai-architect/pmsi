"""应用配置（pydantic-settings，从环境变量/.env 读）。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "dev"
    # 控制库（单一）：租户/用户/SSO/许可
    control_db_dsn: str = "postgresql+asyncpg://pms:pms@localhost:5432/pms_control"
    # Redis：Celery broker + 缓存/锁/限流
    redis_url: str = "redis://localhost:6379/0"
    # 调试期用 header 解析租户；生产走子域/JWT claim（docs/16）
    tenant_header: str = "x-tenant"


settings = Settings()
