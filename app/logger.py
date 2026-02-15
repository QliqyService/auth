import logging
import sys

from loguru import logger as LOGGER

from app.settings import LogLevel


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = LOGGER.level(record.levelname).name
        except (AttributeError, ValueError):
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            if frame.f_back:
                frame = frame.f_back
            depth += 1

        LOGGER.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class CustomLogger:
    LOGGING_LOG_LEVEL = LogLevel.DEBUG
    LOGGING_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"

    @classmethod
    def make_logger(cls) -> LOGGER:
        _logger = cls.customize_logging(level=cls.LOGGING_LOG_LEVEL, logs_format=cls.LOGGING_FORMAT)
        return _logger

    @classmethod
    def customize_logging(cls, level: str, logs_format: str) -> LOGGER:
        intercept_handler = InterceptHandler()

        LOGGER.remove()
        LOGGER.add(
            sink=sys.stdout,
            filter=lambda record: "shared/healthcheck" not in record["message"],
            enqueue=True,
            backtrace=True,
            level=level.upper(),
            format=logs_format,
        )

        lognames = [
            "asyncio",
            "fastapi",
            "uvicorn.access",
            "uvicorn.error",
        ]

        for _log in lognames:
            _logger = logging.getLogger(_log)
            _logger.handlers = [intercept_handler]
            _logger.propagate = False

        return LOGGER.bind(request_id=None, method=None)
