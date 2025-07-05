import logging
import logging.config
from typing import Any, Dict

from pydantic import BaseModel


class LogConfig(BaseModel):
    """Logging configuration"""

    LOGGER_NAME: str = "microarch_ddd"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_LEVEL: str = "INFO"

    # Logging config that you want to customize
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: Dict[str, Any] = {
        "default": {
            "format": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: Dict[str, Any] = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    }
    loggers: Dict[str, Any] = {
        "microarch_ddd": {"handlers": ["default"], "level": LOG_LEVEL},
    }


# Create and configure logger
log_config = LogConfig()
logging_config = log_config.model_dump()
logging.config.dictConfig(logging_config)
logger = logging.getLogger(log_config.LOGGER_NAME)
