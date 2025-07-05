from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select

from core.application.use_cases.queries.base import Query, QueryHandler
from core.domain.model.order_aggregate.order_status import OrderStatusEnum
from core.domain.shared_kernel.location import Location
from infrastructure.adapters.postgres.models.order_aggregate import OrderModel
from infrastructure.adapters.postgres.uow import UnitOfWork


class GetNotCompletedOrdersQuery(Query):
    pass


class NotCompletedOrder(BaseModel):
    id: UUID
    location: Location


class GetNotCompletedOrdersUseCase(QueryHandler):
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def handle(self, query: GetNotCompletedOrdersQuery) -> list[NotCompletedOrder]:
        async with self.uow:
            sql_query = select(OrderModel.id, OrderModel.location).where(
                OrderModel.order_status.in_((OrderStatusEnum.ASSIGNED, OrderStatusEnum.CREATED))
            )
            result = await self.uow.session.execute(sql_query)
            not_completed_orders = result.all()
            return [NotCompletedOrder.model_validate(order, from_attributes=True) for order in not_completed_orders]
