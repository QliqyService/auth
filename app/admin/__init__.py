from pathlib import PosixPath
from typing import Any

import jinja2
import sqladmin
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.datastructures import URL

from app.admin.authentication import AuthenticationBackend
from app.admin.model_views.access_token import AccessTokenAdminView
from app.admin.model_views.users import UserAdminView


__all__ = ["AdminApplication"]


class WAdmin(sqladmin.Admin):
    """Admin interface."""

    def init_templating_engine(self) -> Jinja2Templates:
        """Initialize templating engine."""
        templates = super().init_templating_engine()

        @jinja2.pass_context
        def urlx_for(context: dict, __name: str, **path_params: Any) -> URL:
            """URL for."""
            request: Request = context["request"]
            http_url: URL = request.url_for(__name, **path_params)
            return http_url.replace(scheme="https")

        templates.env.globals["url_for"] = urlx_for
        return templates


class AdminApplication:
    """Admin application."""

    _authentication_backend: AuthenticationBackend
    _admin_app: WAdmin

    def __init__(
        self,
        app: FastAPI,
        engine: AsyncEngine,
        secret_key: str,
        template_dir: PosixPath,
        base_url: str,
        title: str,
    ):
        self._authentication_backend = AuthenticationBackend(
            secret_key=secret_key,
        )
        self._admin_app = WAdmin(
            app=app,
            engine=engine,
            authentication_backend=self._authentication_backend,
            templates_dir=template_dir,  # noqa
            base_url=base_url,
            title=title,
        )

        # Include views
        self.run_startup_actions()

    def run_startup_actions(self) -> None:
        self.include_model_views()

    def include_model_views(self) -> None:
        self._admin_app.add_view(UserAdminView)
        self._admin_app.add_view(AccessTokenAdminView)
