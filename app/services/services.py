import inspect
from typing import Type

from app.services import BaseService
from app.services.broker import BrokerClient
from app.services.mailer import MailerClient
from app.services.postgresql import PostgreSQL

# TODO: пофиксить инициализацию redis
from app.services.redis import RedisClient
from app.services.templates import TemplateFactory
from app.settings import get_settings


class Services:
    config = get_settings()

    database = PostgreSQL(
        username=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
        database=config.POSTGRES_DB,
        echo_pool=config.POSTGRES_ECHO_POOL,
        pool_size=config.POSTGRES_POOL_SIZE,
        connection_retry_period_sec=config.POSTGRES_CONNECTION_RETRY_PERIOD_SEC,
    )
    redis = RedisClient(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        password=config.REDIS_PASSWORD,
        # db=config.REDIS_DB,
    )
    broker = BrokerClient(url=config.RABBITMQ_URL)
    template_factory = TemplateFactory(
        template_dir=config.TEMPLATES_DIR,
    )
    mailer_client = MailerClient(
        broker=broker,
        mailer_prefix=f"{config.APP_STAND}::mailer::",
    )

    @classmethod
    def get_external_services(cls) -> list[Type[BaseService]]:
        """
        Find all class attributes with BaseService subclass
        for using start and stop methods.
        """
        external_services = []
        for _, obj in inspect.getmembers(cls):
            if issubclass(type(obj), BaseService):
                external_services.append(obj)
        return external_services
