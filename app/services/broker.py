from faststream.rabbit import RabbitBroker, RabbitMessage
from loguru import logger as LOGGER

from app.services import BaseService


class BrokerClient(BaseService):
    def __init__(self, url: str, timeout: int = 10):
        self.url = url
        self.broker = RabbitBroker(url=url, timeout=timeout)

    async def start(self):
        await self.broker.connect()
        LOGGER.debug("[Broker Client] Connection initialized.")

    async def stop(self):
        pass

    async def request(self, queue: str, message: dict) -> RabbitMessage | None:
        """Отправка RPC запроса в очередь и получение ответа

        Args:
            queue (str): Очередь, в которую отправляется запрос
            message (dict): Сообщение для отправки

        Returns:
            RabbitMessage: Ответ от удаленного сервиса или None, если ответа нет в течение таймаута
        """
        try:
            return await self.broker.request(queue=queue, message=message)
        except TimeoutError:
            LOGGER.error(f"[Broker Client] Timeout error on request to {queue}")
            return None

    async def publish(self, queue: str, message: dict, reply_to: str | None = None) -> None:
        """Отправка сообщения в очередь

        Args:
            queue (str): Очередь, в которую отправляется сообщение.
            message (dict): Сообщение для отправки.
            reply_to (str | None): Очередь, в которую отправляется ответ на сообщение.
        """
        await self.broker.publish(queue=queue, message=message, reply_to=reply_to)
        LOGGER.debug(f"[Broker Client] Message published to {queue}")
