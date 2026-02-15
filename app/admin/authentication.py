from typing import Optional

import sqladmin.authentication as sqladmin_authentication
from fastapi import Request
from fastapi_users.exceptions import UserNotExists
from loguru import logger as LOGGER

from app.db.models import AccessToken, User
from app.managers import Managers
from app.managers.auth import DatabaseStrategy
from app.managers.users import UserManager
from app.services import Services


__all__ = [
    "AuthenticationBackend",
]


class AuthenticationBackend(sqladmin_authentication.AuthenticationBackend):
    """Admin authentication backend."""

    @staticmethod
    async def get_user_by_credentials(username: str, password: str) -> Optional[User]:
        """Get user by username and password.

        Args:
            username (str): username
            password (str): password
        Returns:
            Optional[User]: user
        """
        async with Services.database.get_session() as session:
            users_db = User.get_db(session=session)
            user_manager = UserManager(users_db)

            try:
                user = await user_manager.get_by_email(user_email=username)
            except UserNotExists:
                return

            if not user.is_superuser:
                return

            verified, _ = user_manager.password_helper.verify_and_update(
                password,
                user.hashed_password,
            )
            if not verified:
                return

        return user

    @staticmethod
    async def get_access_token_strategy() -> DatabaseStrategy:
        """Get access token strategy.

        Returns:
            Managers.auth.DatabaseStrategy: access token strategy
        """
        async with Services.database.get_session() as session:
            access_tokens_db = AccessToken.get_db(session=session)
            return Managers.auth.get_database_strategy(access_tokens_db=access_tokens_db)

    async def create_access_token(self, user: User) -> str:
        """Get access token.

        Args:
            user (User): user
        Returns:
            str: access token
        """
        strategy = await self.get_access_token_strategy()
        return await strategy.write_token(user=user)

    async def get_user_by_access_token(self, access_token: str) -> Optional[User]:
        """Get user by access token.

        Args:
            access_token (str): access token
        Returns:
            Optional[User]: user
        """
        strategy = await self.get_access_token_strategy()
        async with Services.database.get_session() as session:
            users_db = User.get_db(session=session)
            user_manager = UserManager(users_db)

            user = await strategy.read_token(
                token=access_token,
                user_manager=user_manager,
            )
        return user

    async def login(self, request: Request) -> bool:
        """Login user.

        Args:
            request (Request): request
        Returns:
            bool: True if user is logged in
        """

        form = await request.form()
        username, password = form["username"], form["password"]

        user = await self.get_user_by_credentials(username=username, password=password)
        if not user:
            return False

        LOGGER.info(f"[ADMIN] User {username} logged in")

        access_token = await self.create_access_token(user=user)
        request.session.update({"access_token": access_token})
        return True

    async def logout(self, request: Request) -> bool:
        """Logout user.

        Args:
            request (Request): request
        Returns:
            bool: True if user is logged out
        """
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Authenticate user.

        Args:
            request (Request): request
        Returns:
            bool: True if user is authenticated
        """
        access_token = request.session.get("access_token")

        if not access_token:
            LOGGER.warning("Access token not found in session")
            return False

        user = await self.get_user_by_access_token(access_token=access_token)
        if not user:
            LOGGER.warning("User not found by access token")
            return False

        if not user.is_superuser:
            LOGGER.warning(f"User {user.email} is not a superuser")
            return False

        return True
