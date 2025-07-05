from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from api.adapters.background_jobs.assign_orders_job import run_job as run_assign_orders_job
from api.adapters.background_jobs.move_couriers_job import run_job as run_move_couriers_job
from api.logging_config import logger
from infrastructure.di.container import Container


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = Container()
    container.init_resources()
    container.wire(
        modules=["api.lifespan", "api.adapters.background_jobs.assign_orders_job", __name__],
        packages=[
            "api.adapters",  # FastAPI endpoints
            "core.application.use_cases",  # use cases с @inject
        ],
    )  # включая assign_orders_job

    app.state.container = container

    scheduler = AsyncIOScheduler()
    logger.info("Starting scheduler...")
    scheduler.add_job(run_assign_orders_job, trigger="interval", seconds=5)
    scheduler.add_job(run_move_couriers_job, trigger="interval", seconds=5)
    scheduler.start()
    yield
    scheduler.shutdown()
    logger.info("Scheduler shutdown complete")
