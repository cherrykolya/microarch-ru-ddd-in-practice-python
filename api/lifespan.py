import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from api.adapters.background_jobs.assign_orders_job import run_job as run_assign_orders_job
from api.adapters.background_jobs.move_couriers_job import run_job as run_move_couriers_job


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    logging.info("Starting scheduler...")
    scheduler.add_job(run_assign_orders_job, trigger="interval", seconds=2)
    scheduler.add_job(run_move_couriers_job, trigger="interval", seconds=2)
    scheduler.start()
    await app.state.container.init_resources()
    app.state.container.wire(
        modules=[
            "api.adapters.kafka.basket_confirmed.consumer",
            "api.adapters.background_jobs.assign_orders_job",
            "api.adapters.http.controllers",
            __name__,
        ],
    )
    kafka_producer = await app.state.container.kafka_producer()
    await kafka_producer.start()
    yield
    scheduler.shutdown()
    await kafka_producer.stop()
    logging.info("Scheduler shutdown complete")
