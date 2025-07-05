from dependency_injector.wiring import Provide, inject

from core.application.use_cases.commands.assign_orders import AssignOrdersCommand, AssignOrdersUseCase
from infrastructure.di.container import Container

from .base import BaseBackgroundJob


class AssignOrdersJob(BaseBackgroundJob):
    def __init__(
        self,
        use_case: AssignOrdersUseCase,
    ):
        self.use_case = use_case

    async def execute(self):
        await self.use_case.handle(AssignOrdersCommand())


@inject
async def run_job(
    use_case: AssignOrdersUseCase = Provide[Container.assign_orders_use_case],
):
    job = AssignOrdersJob(use_case=use_case)
    await job.execute()
