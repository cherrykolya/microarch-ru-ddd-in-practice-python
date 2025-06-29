from uuid import uuid4

import pytest

from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.model.order_aggregate.order_status import OrderStatusEnum
from core.domain.shared_kernel.location import Location
from infrastructure.adapters.postgres.repositories.courier_repository import CourierRepository
from infrastructure.adapters.postgres.repositories.order_repository import OrderRepository


@pytest.mark.asyncio
async def test_add_order(db_session_with_commit):
    """Тест добавления заказа в репозиторий."""
    # Arrange
    repository = OrderRepository(db_session_with_commit)
    location = Location.create(x=1, y=1)
    order = Order.create(order_id=uuid4(), location=location, volume=100)

    # Act
    saved_order = await repository.add_order(order)

    # Assert
    assert isinstance(saved_order, Order)
    assert saved_order.id == order.id
    assert saved_order.location == order.location
    assert saved_order.volume == order.volume
    assert saved_order.order_status.name == OrderStatusEnum.CREATED
    assert saved_order.courier_id is None


@pytest.mark.asyncio
async def test_get_order(db_session_with_commit):
    """Тест получения заказа из репозитория."""
    # Arrange
    repository = OrderRepository(db_session_with_commit)
    location = Location.create(x=1, y=1)
    order = Order.create(order_id=uuid4(), location=location, volume=100)
    await repository.add_order(order)

    # Act
    retrieved_order = await repository.get_order(order.id)

    # Assert
    assert isinstance(retrieved_order, Order)
    assert retrieved_order.id == order.id
    assert retrieved_order.location == order.location
    assert retrieved_order.volume == order.volume
    assert retrieved_order.order_status.name == OrderStatusEnum.CREATED
    assert retrieved_order.courier_id is None


@pytest.mark.asyncio
async def test_update_order(db_session_with_commit):
    """Тест обновления заказа в репозитории."""
    # Arrange
    repository = OrderRepository(db_session_with_commit)
    location = Location.create(x=1, y=1)
    order = Order.create(order_id=uuid4(), location=location, volume=100)
    saved_order = await repository.add_order(order)

    # Создаем реального курьера в базе данных
    courier_repository = CourierRepository(db_session_with_commit)
    courier = Courier.create(name="Test Courier", location=Location.create(x=1, y=1), speed=10)
    await courier_repository.add_courier(courier)

    # Act
    saved_order.assign(courier.id)  # Меняем статус на ASSIGNED и присваиваем курьера
    await repository.update_order(saved_order)

    # Assert
    updated_order = await repository.get_order(order.id)
    assert isinstance(updated_order, Order)
    assert updated_order.id == order.id
    assert updated_order.location == order.location
    assert updated_order.volume == order.volume
    assert updated_order.order_status.name == OrderStatusEnum.ASSIGNED
    assert updated_order.courier_id == courier.id


@pytest.mark.asyncio
async def test_update_non_existent_order(db_session_with_commit):
    """Тест обновления несуществующего заказа."""
    # Arrange
    repository = OrderRepository(db_session_with_commit)
    location = Location.create(x=1, y=1)
    non_existent_order = Order.create(order_id=uuid4(), location=location, volume=100)

    # Act & Assert
    with pytest.raises(ValueError, match=f"Order with id {non_existent_order.id} not found"):
        await repository.update_order(non_existent_order)


@pytest.mark.asyncio
async def test_order_status_transitions(db_session_with_commit):
    """Тест переходов между статусами заказа."""
    # Arrange
    repository = OrderRepository(db_session_with_commit)
    location = Location.create(x=1, y=1)
    order = Order.create(order_id=uuid4(), location=location, volume=100)
    saved_order = await repository.add_order(order)
    assert saved_order.order_status.name == OrderStatusEnum.CREATED

    # Act & Assert: CREATED -> ASSIGNED
    # Создаем реального курьера в базе данных
    courier_repository = CourierRepository(db_session_with_commit)
    courier = Courier.create(name="Test Courier", location=Location.create(x=1, y=1), speed=10)
    await courier_repository.add_courier(courier)

    saved_order.assign(courier.id)
    await repository.update_order(saved_order)

    updated_order = await repository.get_order(order.id)
    assert updated_order is not None
    assert updated_order.order_status.name == OrderStatusEnum.ASSIGNED
    assert updated_order.courier_id == courier.id

    # Act & Assert: ASSIGNED -> COMPLETED
    updated_order.complete()
    await repository.update_order(updated_order)

    completed_order = await repository.get_order(order.id)
    assert completed_order is not None
    assert completed_order.order_status.name == OrderStatusEnum.COMPLETED
    assert completed_order.courier_id == courier.id


@pytest.mark.asyncio
async def test_get_all_assigned_orders(db_session_with_commit):
    """Тест получения всех назначенных заказов."""
    # Arrange
    repository = OrderRepository(db_session_with_commit)

    # Создаем реального курьера в базе данных
    courier_repository = CourierRepository(db_session_with_commit)
    courier = Courier.create(name="Test Courier", location=Location.create(x=1, y=1), speed=10)
    await courier_repository.add_courier(courier)

    # Создаем заказ со статусом CREATED
    location1 = Location.create(x=1, y=1)
    created_order = Order.create(order_id=uuid4(), location=location1, volume=100)
    await repository.add_order(created_order)

    # Создаем два заказа со статусом ASSIGNED
    location2 = Location.create(x=2, y=2)
    assigned_order1 = Order.create(order_id=uuid4(), location=location2, volume=150)
    assigned_order1.assign(courier.id)
    await repository.add_order(assigned_order1)

    location3 = Location.create(x=3, y=3)
    assigned_order2 = Order.create(order_id=uuid4(), location=location3, volume=200)
    assigned_order2.assign(courier.id)
    await repository.add_order(assigned_order2)

    # Act
    assigned_orders = await repository.get_all_assigned_orders()

    # Assert
    assert len(assigned_orders) == 2
    order_ids = {order.id for order in assigned_orders}
    assert assigned_order1.id in order_ids
    assert assigned_order2.id in order_ids
    assert created_order.id not in order_ids

    for order in assigned_orders:
        assert isinstance(order, Order)
        assert order.order_status.name == OrderStatusEnum.ASSIGNED
        assert order.courier_id == courier.id


@pytest.mark.asyncio
async def test_get_order_not_found(db_session_with_commit):
    """Тест получения несуществующего заказа."""
    # Arrange
    repository = OrderRepository(db_session_with_commit)
    non_existent_id = uuid4()

    # Act
    order = await repository.get_order(non_existent_id)

    # Assert
    assert order is None


@pytest.mark.asyncio
async def test_get_one_created_order_when_none_exists(db_session_with_commit):
    """Тест получения созданного заказа, когда таких нет."""
    # Arrange
    repository = OrderRepository(db_session_with_commit)

    # Act
    order = await repository.get_one_created_order()

    # Assert
    assert order is None


@pytest.mark.asyncio
async def test_get_all_assigned_orders_when_none_exists(db_session_with_commit):
    """Тест получения назначенных заказов, когда таких нет."""
    # Arrange
    repository = OrderRepository(db_session_with_commit)

    # Act
    orders = await repository.get_all_assigned_orders()

    # Assert
    assert isinstance(orders, list)
    assert len(orders) == 0
