from uuid import uuid4

import pytest

from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.courier_aggregate.storage_place import StoragePlace
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.shared_kernel.location import Location
from infrastructure.adapters.postgres.repositories.courier_repository import CourierRepository
from infrastructure.adapters.postgres.repositories.order_repository import OrderRepository


@pytest.mark.asyncio
async def test_add_courier(db_session_with_commit):
    """Тест добавления курьера в репозиторий."""
    # Arrange
    repository = CourierRepository(db_session_with_commit)
    location = Location.create(x=1, y=1)
    courier = Courier.create(
        name="Test Courier",
        location=location,
        speed=10,
    )

    # Act
    saved_courier = await repository.add_courier(courier)

    # Assert
    assert isinstance(saved_courier, Courier)
    assert saved_courier.id == courier.id
    assert saved_courier.name == courier.name
    assert saved_courier.speed == courier.speed
    assert saved_courier.location == courier.location


@pytest.mark.asyncio
async def test_get_courier(db_session_with_commit):
    """Тест получения курьера из репозитория."""
    # Arrange
    repository = CourierRepository(db_session_with_commit)
    location = Location.create(x=1, y=1)
    courier = Courier.create(
        name="Test Courier",
        location=location,
        speed=10,
    )
    await repository.add_courier(courier)

    # Act
    retrieved_courier = await repository.get_courier(courier.id)

    # Assert
    assert isinstance(retrieved_courier, Courier)
    assert retrieved_courier.id == courier.id
    assert retrieved_courier.name == courier.name
    assert retrieved_courier.speed == courier.speed
    assert retrieved_courier.location == courier.location


@pytest.mark.asyncio
async def test_update_courier(db_session_with_commit):
    """Тест обновления курьера в репозитории."""
    # Arrange
    repository = CourierRepository(db_session_with_commit)
    location = Location.create(x=1, y=1)
    courier = Courier.create(
        name="Test Courier",
        location=location,
        speed=10,
    )
    saved_courier = await repository.add_courier(courier)

    # Act
    new_location = Location.create(x=2, y=2)
    saved_courier.name = "Updated Courier"
    saved_courier.speed = 20
    saved_courier.location = new_location
    await repository.update_courier(saved_courier)
    await db_session_with_commit.commit()

    # Assert
    updated_courier = await repository.get_courier(courier.id)
    assert isinstance(updated_courier, Courier)
    assert updated_courier.id == courier.id
    assert updated_courier.name == "Updated Courier"
    assert updated_courier.speed == 20
    assert updated_courier.location == new_location


@pytest.mark.asyncio
async def test_get_free_couriers(db_session_with_commit):
    """Тест получения свободных курьеров."""
    # Arrange
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
    order_repository = OrderRepository(db_session_with_commit)
    order = await order_repository.add_order(order)

    # Добавляем дополнительное место хранения с заказом
    storage_place = StoragePlace.create_storage_place(
        name="Storage 1",
        total_volume=100,
    )
    storage_place.store(order.id, 50)  # Используем ID созданного заказа
    courier3.storage_places.append(storage_place)

    repository = CourierRepository(db_session_with_commit)
    await repository.add_courier(courier1)
    await repository.add_courier(courier2)
    await repository.add_courier(courier3)

    # Act
    free_couriers = await repository.get_all_free_couriers()

    # Assert
    assert len(free_couriers) == 2
    courier_ids = {courier.id for courier in free_couriers}
    assert courier1.id in courier_ids
    assert courier2.id in courier_ids
    assert courier3.id not in courier_ids
