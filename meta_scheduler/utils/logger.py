import logging

from glogger import logger  # type: ignore
from meta_scheduler import settings


def get_logger(name: str) -> logging.Logger:
    return logger.get_logger(
        name, logging.DEBUG if settings.scheduler.DEBUG else logging.INFO
    )
