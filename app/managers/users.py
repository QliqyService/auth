import uuid
from typing import TYPE_CHECKING, Any, Final, Optional
from urllib.parse import urlencode

from fastapi_users import BaseUserManager, UUIDIDMixin, models
from fastapi_users.jwt import generate_jwt
from loguru import logger as LOGGER

from app.db.models import User
from app.services import Services
from app.settings import get_settings


if TYPE_CHECKING:
    from fastapi import Request


settings = get_settings()

VERIFY_TEMPLATE_PATH: Final[str] = "email/verify.html"
RESET_PASSWORD_TEMPLATE_PATH: Final[str] = "email/reset_password.html"


def build_frontend_url(path: str, **query_params: str) -> str:
    base_url = settings.FRONTEND_BASE_URL
    query = urlencode({key: value for key, value in query_params.items() if value})
    return f"{base_url}{path}" + (f"?{query}" if query else "")


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.RESET_PASSWORD_TOKEN_SECRET
    reset_password_token_lifetime_seconds = settings.RESET_PASSWORD_TOKEN_LIFETIME_SECONDS

    verification_token_lifetime_seconds = settings.VERIFICATION_TOKEN_LIFETIME_SECONDS
    verification_token_secret = settings.VERIFICATION_TOKEN_SECRET

    async def on_after_register(self, user: User, request: Optional["Request"] = None) -> None:
        LOGGER.warning(f"User {user.id} has registered.")

        is_auto_verify = request.query_params.get("is_auto_verify")
        if is_auto_verify is not None and is_auto_verify != "false":
            await self.user_db.update(user, {"is_verified": True})
            LOGGER.warning(f"User {user.id} has auto-verified their email.")
            return

        # 1. Generate a verification token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )

        # 2. Render verification email template
        redirect_url = build_frontend_url(
            "/verify-email",
            token=token,
            email=user.email,
        )
        html_message = await Services.template_factory.render(
            template_path=VERIFY_TEMPLATE_PATH,
            context=dict(
                user=user,
                url=redirect_url,
            ),
        )

        # 3. Send verification email
        await Services.mailer_client.push_message(
            recipients=[user.email],
            subject="Verify your email",
            html_message=html_message,
        )

    async def on_after_forgot_password(self, user: User, token: str, request: Optional["Request"] = None) -> None:
        LOGGER.warning(f"User {user.id} has forgot their password. Reset token: {token}")

        # 1. Render reset password email template
        redirect_url = build_frontend_url(
            "/reset-password",
            token=token,
            email=user.email,
        )
        html_message = await Services.template_factory.render(
            template_path=RESET_PASSWORD_TEMPLATE_PATH,
            context=dict(
                user=user,
                url=redirect_url,
            ),
        )

        # 2. Send forgot password email
        await Services.mailer_client.push_message(
            recipients=[user.email],
            subject="Reset your password",
            html_message=html_message,
        )

    async def on_after_request_verify(self, user: User, token: str, request: Optional["Request"] = None) -> None:
        LOGGER.warning(f"Verification requested for user {user.id}. Verification token: {token}")

        # 1. Render verification email template
        redirect_url = build_frontend_url(
            "/verify-email",
            token=token,
            email=user.email,
        )
        html_message = await Services.template_factory.render(
            template_path=VERIFY_TEMPLATE_PATH,
            context=dict(
                user=user,
                url=redirect_url,
            ),
        )

        # 2. Send verification email
        await Services.mailer_client.push_message(
            recipients=[user.email],
            subject="Verify your email",
            html_message=html_message,
        )

    async def on_after_update(
        self,
        user: models.UP,
        update_dict: dict[str, Any],
        request: Optional["Request"] = None,
    ) -> None:
        LOGGER.warning(f"User {user.id} has updated their profile.")

        if not update_dict.get("email"):
            return

        # 1. Generate a verification token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )

        # 2. Render verification email template
        redirect_url = build_frontend_url(
            "/verify-email",
            token=token,
            email=user.email,
        )
        html_message = await Services.template_factory.render(
            template_path=VERIFY_TEMPLATE_PATH,
            context=dict(
                user=user,
                url=redirect_url,
            ),
        )

        # 3. Send verification email
        await Services.mailer_client.push_message(
            recipients=[user.email],
            subject="Verify your email",
            html_message=html_message,
        )
