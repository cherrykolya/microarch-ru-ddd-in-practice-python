from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.application.use_cases.queries.base import Query, QueryHandler
from core.domain.shared_kernel.location import Location
from infrastructure.adapters.postgres.models.courier_aggregate import CourierModel, StoragePlaceModel


class GetAllBusyCouriersQuery(Query):
    pass


class BusyCourier(BaseModel):
    id: UUID
    name: str
    location: Location


class GetAllBusyCouriersUseCase(QueryHandler):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, query: GetAllBusyCouriersQuery) -> list[BusyCourier]:
        sql_query = (
            select(CourierModel.id, CourierModel.name, CourierModel.location)
            .outerjoin(CourierModel.storage_places)
            .group_by(CourierModel.id)
            .having(func.count(StoragePlaceModel.order_id) != 0)
            .execution_options(populate_existing=True)
        )

        result = await self.session.execute(sql_query)
        busy_couriers = result.all()
        # TODO: здесь сделать правильную валдиацию
        return [BusyCourier.model_validate(courier, from_attributes=True) for courier in busy_couriers]
