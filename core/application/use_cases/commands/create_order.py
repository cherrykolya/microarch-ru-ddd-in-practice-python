from uuid import UUID

from core.application.use_cases.commands.base import Command, CommandHandler
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.shared_kernel.location import Location
from core.ports.order_repository_interface import OrderRepositoryInterface
from core.ports.unit_of_work import UnitOfWork


class CreateOrderCommand(Command):
    basket_id: UUID
    street: str
    volume: int


class CreateOrderUseCase(CommandHandler):
    def __init__(self, order_repository: OrderRepositoryInterface, uow: UnitOfWork):
        self.order_repository = order_repository
        self.uow = uow

    async def handle(self, command: CreateOrderCommand) -> None:
        async with self.uow:
            order = await self.order_repository.get_order(command.basket_id)
            if order:
                raise ValueError("Order already exists")

            location = Location.create_random()  # TODO: get location from street

            order = Order.create(command.basket_id, location, command.volume)
            await self.order_repository.add_order(order)
