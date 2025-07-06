from core.application.use_cases.commands.base import Command, CommandHandler
from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.shared_kernel.location import Location
from core.ports.unit_of_work import UnitOfWork


class CreateCourierCommand(Command):
    name: str
    speed: int


class CreateCourierUseCase(CommandHandler):
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def handle(self, command: CreateCourierCommand) -> None:
        async with self.uow:
            courier = Courier.create(command.name, command.speed, Location.create_random())
            await self.uow.courier_repository.add_courier(courier)
