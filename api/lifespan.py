from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from api.adapters.background_jobs.assign_orders_job import run_job as run_assign_orders_job
from api.adapters.background_jobs.move_couriers_job import run_job as run_move_couriers_job
from api.logging_config import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    logger.info("Starting scheduler...")
    scheduler.add_job(run_assign_orders_job, trigger="interval", seconds=2)
    scheduler.add_job(run_move_couriers_job, trigger="interval", seconds=2)
    scheduler.start()
    yield
    scheduler.shutdown()
    logger.info("Scheduler shutdown complete")
