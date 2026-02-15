import json
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Annotated, Optional
from uuid import UUID

from fastapi import Depends
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy import DatabaseStrategy as IDatabaseStrategy
from fastapi_users.exceptions import InvalidID, UserNotExists
from fastapi_users.manager import BaseUserManager
from fastapi_users.models import ID, UP
from loguru import logger as LOGGER

from app.db.models import User
from app.db.models.access_tokens import AccessToken
from app.dependencies import get_access_tokens_db
from app.schemas.auth import PerpetualTokenResponse
from app.services import Services
from app.settings import get_settings


if TYPE_CHECKING:
    from fastapi_users.authentication.strategy.db import AccessTokenDatabase


SETTINGS = get_settings()


class DatabaseStrategy(IDatabaseStrategy):
    @staticmethod
    def now():
        return datetime.now(timezone.utc).replace(tzinfo=None)

    @staticmethod
    async def read_token_from_cache(token: Optional[str]) -> Optional[UP]:
        """Read token from cache

        Args:
            token (Optional[str]): token to read
        Returns:
            Optional[UP]: token read from cache
        """
        try:
            cached_data = await Services.redis.get(key=f"{SETTINGS.REDIS_CACHED_TOKEN_PREFIX}{token}")
            if cached_data:
                return User(
                    id=UUID(cached_data["id"]),
                    email=cached_data["email"],
                    is_active=cached_data["is_active"],
                    is_verified=cached_data["is_verified"],
                    is_superuser=cached_data["is_superuser"],
                )
        except Exception as ex:
            LOGGER.exception(ex)

    async def read_token(
        self,
        token: Optional[str],
        user_manager: BaseUserManager[UP, ID],
    ) -> Optional[UP]:
        if token is None:
            return None

        user_from_cache = await self.read_token_from_cache(token=token)
        if user_from_cache:
            return user_from_cache

        max_age = None
        if self.lifetime_seconds:
            max_age = self.now() - timedelta(seconds=self.lifetime_seconds)

        access_token = await self.database.get_by_token(token, max_age)
        if access_token is None:
            return None

        try:
            parsed_id = user_manager.parse_id(access_token.user_id)
            return await user_manager.get(parsed_id)
        except (UserNotExists, InvalidID):
            return None

    async def write_token_to_cache(self, user: UP, token: Optional[str]) -> None:
        """Write token to cache

        Args:
            user (UP): user
            token (Optional[str]): token to write
        Returns:
            None
        """
        try:
            await Services.redis.set(
                key=f"{SETTINGS.REDIS_CACHED_TOKEN_PREFIX}{token}",
                value=json.dumps(
                    {
                        "id": str(user.id),
                        "email": user.email,
                        "is_active": user.is_active,
                        "is_verified": user.is_verified,
                        "is_superuser": user.is_superuser,
                    }
                ),
                ttl=self.lifetime_seconds,
            )
        except Exception as ex:
            LOGGER.exception(ex)

    async def write_token(self, user: UP) -> str:
        token = await super().write_token(user=user)
        await self.write_token_to_cache(user=user, token=token)
        return token

    @staticmethod
    async def destroy_token_from_cache(token: str) -> None:
        """Destroy token from cache

        Args:
            token (Optional[str]): token to destroy
        """

        try:
            await Services.redis.delete(key=f"{SETTINGS.REDIS_CACHED_TOKEN_PREFIX}{token}")
        except Exception as ex:
            LOGGER.exception(ex)

    async def destroy_token(self, token: str, user: UP) -> None:
        await super().destroy_token(token=token, user=user)
        await self.destroy_token_from_cache(token=token)


class AuthManager:
    def __init__(self):
        self.bearer_transport = BearerTransport(tokenUrl=SETTINGS.BEARER_TOKEN_URL)
        self.access_token_lifetime_seconds = SETTINGS.ACCESS_TOKEN_LIFETIME_SECONDS
        self.authentication_backend = AuthenticationBackend(
            name="access-tokens-db",
            transport=self.bearer_transport,
            get_strategy=self.get_database_strategy,
        )

    def get_database_strategy(
        self,
        access_tokens_db: Annotated["AccessTokenDatabase[AccessToken]", Depends(get_access_tokens_db)],
    ) -> DatabaseStrategy:
        return DatabaseStrategy(
            database=access_tokens_db,
            lifetime_seconds=self.access_token_lifetime_seconds,
        )

    async def _generate_perpetual_token(self, user_id: UUID) -> Optional[str]:
        """Generate a perpetual token for the user.

        Args:
            user_id (UUID): The ID of the user.

        Returns:
            Optional[str]: The generated token or None if it fails.
        """

        async with Services.database.session() as session:
            users_db = User.get_db(session=session)

            exists_user = await users_db.get(id=user_id)
            if not exists_user:
                return None

            access_tokens_db = AccessToken.get_db(session=session)
            strategy = self.get_database_strategy(access_tokens_db=access_tokens_db)

            return await strategy.write_token(user=exists_user)

    async def generate_perpetual_token(self, user_id: UUID) -> PerpetualTokenResponse:
        """Generate a perpetual token for the user.

        Args:
            user_id (UUID): ID of the user for whom to generate the token.

        Returns:
            PerpetualTokenResponse: Response containing the generated token.
        """
        access_token = await self._generate_perpetual_token(user_id=user_id)
        if access_token is None:
            raise UserNotExists(f"User with ID {user_id} does not exist or token generation failed.")
        return PerpetualTokenResponse(access_token=access_token)
