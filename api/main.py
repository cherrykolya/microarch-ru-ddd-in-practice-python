import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.adapters.http.controllers import router
from api.config import get_settings
from api.lifespan import lifespan
from api.logging_config import log_config, logger
from infrastructure.di.container import Container


def get_application() -> FastAPI:
    settings = get_settings()

    container = Container()
    container.init_resources()
    container.wire(
        modules=[
            "api.lifespan",
            "api.adapters.background_jobs.assign_orders_job",
            __name__,
            "api.adapters.http.controllers",
        ],
    )  # включая assign_orders_job

    # Configure FastAPI logging
    logging.getLogger("uvicorn.access").handlers = logging.getLogger(log_config.LOGGER_NAME).handlers
    logging.getLogger("uvicorn.error").handlers = logging.getLogger(log_config.LOGGER_NAME).handlers

    logger.info("Initializing FastAPI application...")
    application = FastAPI(**settings.model_dump(), lifespan=lifespan)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.state.container = container

    application.include_router(router)

    return application


app = get_application()
