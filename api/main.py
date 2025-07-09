import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.adapters.http.controllers import router
from api.adapters.kafka.basket_confirmed.consumer import router as router_kafka
from api.config import get_settings
from api.lifespan import lifespan
from infrastructure.di.container import Container


def get_application() -> FastAPI:
    settings = get_settings()

    container = Container()
    container.init_resources()
    container.wire(
        modules=[
            "api.adapters.kafka.basket_confirmed.consumer",
            "api.adapters.background_jobs.assign_orders_job",
            "api.adapters.http.controllers",
            __name__,
        ],
    )

    logging.info("Initializing FastAPI application...")
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
    application.include_router(router_kafka)

    return application


app = get_application()
