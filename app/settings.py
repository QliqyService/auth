from enum import StrEnum
from functools import lru_cache
from pathlib import Path, PosixPath

from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AppStand(StrEnum):
    DEV = "dev"
    RC = "rc"
    PROD = "prod"
    DEMO = "demo"
    TEST = "test"
    LOCAL = "local"


class _Settings(BaseSettings):
    """General service settings"""

    ROOT_DIR: PosixPath = Path(__file__).parent.parent
    APP_DIR: PosixPath = ROOT_DIR / "app"
    TEMPLATES_DIR: PosixPath = APP_DIR / "templates"
    ADMIN_TEMPLATES_DIR: PosixPath = TEMPLATES_DIR / "admin"

    APP_TITLE: str = "Auth Service"
    APP_DESCRIPTION: str = "Authentication and authorization service"

    APP_DEBUG: bool = False
    APP_PUBLIC_PATH: str | None = None
    APP_STAND: AppStand = AppStand.LOCAL
    APP_RELEASE: str = "not-set"
    APP_SECRET_KEY: str = "7b948a7691e1f3155b3c82f7df1e383793cf67f4232e28640d51a90f4b50dbfb"
    APP_NAME: str = "auth"

    BEARER_TOKEN_URL: str = "api/v1/auth/login"

    ACCESS_TOKEN_LIFETIME_SECONDS: int = 60 * 60 * 24 * 7  # 1 week
    VERIFICATION_TOKEN_LIFETIME_SECONDS: int = 60 * 15  # 15 minutes
    RESET_PASSWORD_TOKEN_LIFETIME_SECONDS: int = 60 * 15  # 15 minutes

    VERIFICATION_TOKEN_SECRET: str = "6f071bc0889670163b78df25df5774a5b44512f6077e1e6542074e7b9aa8b145"
    RESET_PASSWORD_TOKEN_SECRET: str = "8bee6b5e2f90d49a5cf6f8e152060f056ede2c211b728d6d008c91dcc3f3c9c4"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_POOL_SIZE: int = 10
    POSTGRES_ECHO_POOL: str | bool = False
    POSTGRES_CONNECTION_RETRY_PERIOD_SEC: float = 5.0

    @property
    def POSTGRES_URL(self) -> str:
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )

    @property
    def RABBITMQ_URL(self) -> str:
        return "amqp://{}:{}@{}:{}?name={}".format(
            self.RABBITMQ_USER,
            self.RABBITMQ_PASSWORD,
            self.RABBITMQ_HOST,
            self.RABBITMQ_PORT,
            self.APP_NAME,
        )

    POSTGRES_NAMING_CONVENTION: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str | None = None
    REDIS_DB: str | int | None = None
    REDIS_CACHED_TOKEN_PREFIX: str = "token::"

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    MAILER_ROUTING_KEY: str = "mailer_requests"
    REDIRECT_URI: str = "https://qliqy.io/"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings(env_file: str = ".env") -> _Settings:
    return _Settings(_env_file=env_file)
