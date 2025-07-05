import logging

from core.application.use_cases.commands.base import Command, CommandHandler
from core.domain.services.dispatch_service_interface import DispatcherInterface
from core.ports.unit_of_work import UnitOfWork


class AssignOrdersCommand(Command):
    pass


class AssignOrdersUseCase(CommandHandler):
    def __init__(
        self,
        uow: UnitOfWork,
        dispatcher: DispatcherInterface,
    ):
        self.uow = uow
        self.dispatcher = dispatcher

    async def handle(self, command: AssignOrdersCommand):
        async with self.uow:
            order = await self.uow.order_repository.get_one_created_order()
            if order is None:
                logging.error("No created order found")
                return

            couriers = await self.uow.courier_repository.get_all_free_couriers()
            if len(couriers) == 0:
                logging.error("No free couriers found")
                return

            closest_courier = self.dispatcher.dispatch(couriers, order)

            await self.uow.order_repository.update_order(order)
            await self.uow.courier_repository.update_courier(closest_courier)
