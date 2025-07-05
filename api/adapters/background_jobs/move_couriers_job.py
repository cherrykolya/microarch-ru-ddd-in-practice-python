from dependency_injector.wiring import Provide, inject

from core.application.use_cases.commands.move_couriers import MoveCouriersCommand, MoveCouriersUseCase
from infrastructure.di.container import Container

from .base import BaseBackgroundJob


class MoveCouriersJob(BaseBackgroundJob):
    def __init__(
        self,
        use_case: MoveCouriersUseCase,
    ):
        self.use_case = use_case

    async def execute(self):
        await self.use_case.handle(MoveCouriersCommand())


@inject
async def run_job(
    use_case: MoveCouriersUseCase = Provide[Container.move_couriers_use_case],
):
    job = MoveCouriersJob(use_case=use_case)
    await job.execute()
