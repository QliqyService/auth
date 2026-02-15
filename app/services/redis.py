import json
from typing import Any, Optional

from loguru import logger as LOGGER
from redis.asyncio import ConnectionPool, Redis

from app.services import BaseService


class RedisClient(BaseService):
    _host: str
    _port: int
    _password: str | None
    _connection_pool: ConnectionPool | None

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: str | None = None,
        db: int | str | None = None,
    ):
        super().__init__()
        self._host = host
        self._port = port
        self._password = password
        self._connection_pool = ConnectionPool(
            host=self._host,
            port=self._port,
            password=password,
            db=db,
        )

    def get_client(self) -> Redis:
        return Redis(connection_pool=self._connection_pool)

    async def start(self):
        """
        Run actions for starting a service
        """
        async with self.get_client() as client:
            if not await client.ping():
                LOGGER.error(f"[Redis Client] Connection error: {self._host}:{self._port}")
            LOGGER.debug(f"[Redis Client] Connection initialized: {self._host}:{self._port}")

    async def stop(self):
        """
        Run actions for stopping a service
        """
        pass

    async def healthcheck(self) -> tuple[bool, str]:
        try:
            async with self.get_client() as client:
                is_working, reason = await client.ping() is not None, ""
                if not is_working:
                    reason = "Connection error"
        except Exception as err:
            is_working, reason = False, str(err)
        return is_working, reason

    async def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        async with self.get_client() as client:
            data = await client.get(key)

        if data:
            return json.loads(data)

        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value into cache."""
        async with self.get_client() as client:
            if ttl:
                return await client.setex(key, ttl, value)

            return await client.set(key, value)

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self.get_client() as client:
            return await client.delete(key)
