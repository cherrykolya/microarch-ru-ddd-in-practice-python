import logging

from core.application.use_cases.commands.base import Command, CommandHandler
from core.ports.unit_of_work import UnitOfWork


class MoveCouriersCommand(Command):
    pass


class MoveCouriersUseCase(CommandHandler):
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    async def handle(self, command: MoveCouriersCommand) -> None:
        async with self.uow:
            orders = await self.uow.order_repository.get_all_assigned_orders()
            for order in orders:
                if not order.courier_id:
                    logging.info(f"Order {order.id} has no courier")
                    continue

                courier = await self.uow.courier_repository.get_courier(order.courier_id)
                if not courier:
                    logging.info(f"Courier {order.courier_id} not found")
                    continue

                courier.move_towards(order.location)

                if courier.location == order.location:
                    courier.complete_order(order)
                    await self.uow.order_repository.update_order(order)

                await self.uow.courier_repository.update_courier(courier)
