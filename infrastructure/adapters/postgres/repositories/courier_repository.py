from uuid import UUID, uuid4

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.ports.courier_repository_interface import CourierRepositoryInterface
from infrastructure.adapters.postgres.models.courier_aggregate import (
    CourierModel,
    CourierStoragePlaceModel,
    StoragePlaceModel,
)


class CourierRepository(CourierRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_courier(self, courier: Courier) -> Courier:
        # Первый flush: добавляем курьера одним запросом
        courier_values = {
            "id": courier.id,
            "name": courier.name,
            "speed": courier.speed,
            "location": courier.location.model_dump(),
        }
        stmt = insert(CourierModel).values(courier_values).returning(CourierModel)
        result = await self.session.execute(stmt)
        courier_model = result.unique().scalar_one()

        # Второй flush: добавляем места хранения одним запросом
        if courier.storage_places:
            storage_place_values = [
                {"id": sp.id, "name": sp.name, "total_volume": sp.total_volume, "order_id": sp.order_id}
                for sp in courier.storage_places
            ]
            stmt = insert(StoragePlaceModel).values(storage_place_values)
            await self.session.execute(stmt)

            # Третий flush: добавляем связи курьер-место хранения одним запросом
            courier_storage_values = [
                {"id": uuid4(), "courier_id": courier.id, "storage_place_id": sp.id} for sp in courier.storage_places
            ]
            stmt = insert(CourierStoragePlaceModel).values(courier_storage_values)
            await self.session.execute(stmt)

        await self.session.refresh(courier_model, ["storage_places"])
        return courier_model.to_domain_object()

    async def update_courier(self, courier: Courier) -> None:
        existing_courier = await self._get_courier_model(courier.id)
        if not existing_courier:
            raise ValueError(f"Courier with id {courier.id} not found")

        # Обновляем основные поля курьера
        existing_courier.name = courier.name
        existing_courier.speed = courier.speed
        existing_courier.location = courier.location.model_dump()

        # Получаем существующие места хранения
        existing_storage_places = {sp.id: sp for sp in existing_courier.storage_places}
        new_storage_places = {sp.id: sp for sp in courier.storage_places} if courier.storage_places else {}

        # Определяем какие связи нужно добавить, а какие удалить
        to_add = set(new_storage_places.keys()) - set(existing_storage_places.keys())
        to_remove = set(existing_storage_places.keys()) - set(new_storage_places.keys())
        to_update = set(existing_storage_places.keys()) & set(new_storage_places.keys())

        if to_remove:
            # Удаляем только те связи, которых нет в новом наборе
            delete_query = delete(CourierStoragePlaceModel).where(
                CourierStoragePlaceModel.courier_id == courier.id,
                CourierStoragePlaceModel.storage_place_id.in_(to_remove),
            )
            await self.session.execute(delete_query)

        if to_add:
            # Создаем только новые места хранения
            new_storage_place_values = [
                {"id": sp.id, "name": sp.name, "total_volume": sp.total_volume, "order_id": sp.order_id}
                for sp_id, sp in new_storage_places.items()
                if sp_id in to_add
            ]
            if new_storage_place_values:
                stmt = insert(StoragePlaceModel).values(new_storage_place_values)
                await self.session.execute(stmt)

            # Создаем только новые связи
            new_courier_storage_values = [
                {"id": uuid4(), "courier_id": courier.id, "storage_place_id": sp_id} for sp_id in to_add
            ]
            stmt = insert(CourierStoragePlaceModel).values(new_courier_storage_values)
            await self.session.execute(stmt)

        if to_update:
            # Обновляем существующие места хранения
            for sp_id in to_update:
                new_sp = new_storage_places[sp_id]
                existing_sp = existing_storage_places[sp_id]

                # Обновляем только если есть изменения
                if (
                    existing_sp.name != new_sp.name
                    or existing_sp.total_volume != new_sp.total_volume
                    or existing_sp.order_id != new_sp.order_id
                ):
                    update_query = (
                        update(StoragePlaceModel)
                        .where(StoragePlaceModel.id == sp_id)
                        .values(name=new_sp.name, total_volume=new_sp.total_volume, order_id=new_sp.order_id)
                    )
                    await self.session.execute(update_query)

        await self.session.refresh(existing_courier, ["storage_places"])

    async def get_courier(self, courier_id: UUID) -> Courier | None:
        courier_model = await self._get_courier_model(courier_id)
        return courier_model.to_domain_object() if courier_model else None

    async def get_all_free_couriers(self) -> list[Courier]:
        query = (
            select(CourierModel)
            .outerjoin(CourierModel.storage_places)
            .group_by(CourierModel.id)
            .having(func.count(StoragePlaceModel.order_id) == 0)
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(query)
        free_couriers = result.unique().scalars().all()
        return [courier_model.to_domain_object() for courier_model in free_couriers]

    async def _get_courier_model(self, courier_id: UUID) -> CourierModel | None:
        """Вспомогательный метод для получения модели курьера с загруженными связями."""
        query = select(CourierModel).filter(CourierModel.id == courier_id).execution_options(populate_existing=True)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()
