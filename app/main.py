from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from loguru import logger as LOGGER
from starlette.middleware.cors import CORSMiddleware

from app.admin import AdminApplication
from app.logger import CustomLogger
from app.router.router import api_router
from app.services import Services
from app.settings import get_settings


class Application(FastAPI):
    def __init__(self):
        self.services = Services()
        self.settings = get_settings()
        self.logger = CustomLogger.make_logger()

        super().__init__(
            title=self.settings.APP_TITLE,
            root_path_in_servers=True,
            root_path=self.settings.APP_PUBLIC_PATH,
            docs_url="/api",
            redoc_url="/api/docs",
            openapi_url="/api/openapi.json",
            default_response_class=ORJSONResponse,
            version=self.settings.APP_RELEASE,
        )
        self.run_startup_actions()

        self.admin = AdminApplication(
            app=self,
            engine=self.services.database.get_engine(),
            secret_key=self.settings.APP_SECRET_KEY,
            template_dir=self.settings.ADMIN_TEMPLATES_DIR,
            base_url=f"{self.settings.APP_PUBLIC_PATH}/admin",
            title=self.settings.APP_TITLE,
        )

    def run_startup_actions(self) -> None:
        self.add_middlewares()
        self.add_startup_event_handlers()
        self.add_shutdown_event_handlers()
        self.include_routers()

    def include_routers(self) -> None:
        self.include_router(api_router)
        LOGGER.debug("[MAIN] Routers added")

    def add_middlewares(self) -> None:
        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        LOGGER.debug("[MAIN] Middlewares added")

    def add_startup_event_handlers(self) -> None:
        for service in self.services.get_external_services():
            self.add_event_handler("startup", service.start)
            LOGGER.debug(f"[MAIN] Startup event handler added: {service}")

    def add_shutdown_event_handlers(self) -> None:
        for service in self.services.get_external_services():
            self.add_event_handler("shutdown", service.stop)


app = Application()
