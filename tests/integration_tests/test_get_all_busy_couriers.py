from uuid import uuid4

import pytest

from core.application.use_cases.queries.get_all_busy_couriers import GetAllBusyCouriersQuery
from core.domain.model.courier_aggregate.courier_aggregate import Courier, StoragePlace
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.shared_kernel.location import Location
from infrastructure.adapters.postgres.repositories.courier_repository import CourierRepository
from infrastructure.adapters.postgres.repositories.order_repository import OrderRepository
from infrastructure.di.container import Container


@pytest.mark.asyncio
async def test_get_all_busy_couriers(test_container: Container):
    uow = test_container.unit_of_work()
    get_all_busy_couriers = test_container.get_all_busy_couriers_use_case()

    async with uow:
        # Создать занятого курьера в бд
        courier_repository: CourierRepository = uow.courier_repository
        order_repository: OrderRepository = uow.order_repository

        location1 = Location.create(x=5, y=5)
        courier1 = Courier.create(
            name="Free Courier 1",
            speed=10,
            location=location1,
        )

        location2 = Location.create(x=3, y=3)
        courier2 = Courier.create(
            name="Free Courier 2",
            speed=15,
            location=location2,
        )

        location3 = Location.create(x=7, y=7)
        courier3 = Courier.create(
            name="Busy Courier",
            speed=20,
            location=location3,
        )

        # Создаем заказ через репозиторий
        order_location = Location.create(x=8, y=8)
        order = Order.create(order_id=uuid4(), location=order_location, volume=50)
        order = await order_repository.add_order(order)

        # Добавляем дополнительное место хранения с заказом
        storage_place = StoragePlace.create_storage_place(
            name="Storage 1",
            total_volume=100,
        )
        storage_place.store(order.id, 50)  # Используем ID созданного заказа
        courier3.storage_places.append(storage_place)

        await courier_repository.add_courier(courier1)
        await courier_repository.add_courier(courier2)
        await courier_repository.add_courier(courier3)

        # Используем use case
        result = await get_all_busy_couriers.handle(GetAllBusyCouriersQuery())

        assert result is not None
