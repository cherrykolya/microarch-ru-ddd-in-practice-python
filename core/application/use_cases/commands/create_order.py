from uuid import UUID

from core.application.use_cases.commands.base import Command, CommandHandler
from core.domain.model.order_aggregate.order_aggregate import Order
from core.ports.geo_service_interface import GeoServiceInterface
from core.ports.unit_of_work import UnitOfWork


class CreateOrderCommand(Command):
    basket_id: UUID
    street: str
    volume: int


class CreateOrderUseCase(CommandHandler):
    def __init__(self, uow: UnitOfWork, geo_service: GeoServiceInterface):
        self.uow = uow
        self.geo_service = geo_service

    async def handle(self, command: CreateOrderCommand) -> None:
        async with self.uow:
            order = await self.uow.order_repository.get_order(command.basket_id)
            if order:
                raise ValueError("Order already exists")

            location = await self.geo_service.get_location(command.street)

            order = Order.create(command.basket_id, location, command.volume)
            await self.uow.order_repository.add_order(order)
