from typing import Sequence
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select

from core.application.use_cases.queries.base import Query, QueryHandler
from core.domain.shared_kernel.location import Location
from infrastructure.adapters.postgres.models.courier_aggregate import CourierModel
from infrastructure.adapters.postgres.uow import UnitOfWork


class GetAllCouriersQuery(Query):
    pass


class Courier(BaseModel):
    id: UUID
    name: str
    location: Location


class GetAllCouriersUseCase(QueryHandler):
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def handle(self, query: GetAllCouriersQuery) -> Sequence[Courier]:
        async with self.uow:
            sql_query = (
                select(CourierModel.id, CourierModel.name, CourierModel.location)
                .outerjoin(CourierModel.storage_places)
                .execution_options(populate_existing=True)
            )

            result = await self.uow.session.execute(sql_query)
            couriers = result.all()
            # TODO: здесь сделать правильную валдиацию
            return [Courier.model_validate(courier, from_attributes=True) for courier in couriers]
