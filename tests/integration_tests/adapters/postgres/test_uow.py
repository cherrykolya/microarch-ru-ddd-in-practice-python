from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from core.domain.events.base import OrderStatusChangedEvent
from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.model.order_aggregate.order_status import OrderStatus
from core.domain.shared_kernel.location import Location
from infrastructure.di.container import Container


@pytest.fixture
def mock_event_publisher():
    mock = AsyncMock()
    mock.requires_commit_after_publish = False
    return mock


@pytest.mark.asyncio
async def test_uow_publishes_events_on_commit(test_container: Container, mock_event_publisher):
    # Arrange
    test_container.kafka_event_publisher.override(mock_event_publisher)
    order_id = uuid4()

    # Act
    async with test_container.unit_of_work() as uow:
        # Имитируем создание заказа, который должен опубликовать событие
        order = Order.create(order_id=order_id, location=Location.create(x=5, y=5), volume=1)
        await uow.order_repository.add_order(order)

    # Assert
    mock_event_publisher.publish.assert_called_once()
    published_events = mock_event_publisher.publish.call_args[0][0]
    assert len(published_events) == 1

    event = published_events[0]
    assert isinstance(event, OrderStatusChangedEvent)
    assert event.order_id == order_id
    assert event.order_status == OrderStatus.created()


@pytest.mark.asyncio
async def test_uow_does_not_publish_events_on_rollback(test_container: Container, mock_event_publisher):
    # Arrange
    test_container.kafka_event_publisher.override(mock_event_publisher)
    order_id = uuid4()

    # Act
    with pytest.raises(ValueError, match="Test exception"):
        async with test_container.unit_of_work() as uow:
            # Имитируем создание заказа, который должен вызвать ошибку
            order = Order.create(order_id=order_id, location=Location.create(x=5, y=5), volume=1)
            await uow.order_repository.add_order(order)
            raise ValueError("Test exception")

    # Assert
    mock_event_publisher.publish.assert_not_called()


@pytest.mark.asyncio
async def test_uow_publishes_multiple_events_in_order(test_container: Container, mock_event_publisher):
    # Arrange
    test_container.kafka_event_publisher.override(mock_event_publisher)
    order_id = uuid4()

    async with test_container.unit_of_work() as uow:
        # создаем курьера
        location = Location.create(x=1, y=1)
        courier = Courier.create(
            name="Test Courier",
            location=location,
            speed=10,
        )

        await uow.courier_repository.add_courier(courier)
        # Создаем заказ и назначаем курьера - должно быть два события
        order = Order.create(order_id=order_id, location=Location.create(x=5, y=5), volume=1)
        await uow.order_repository.add_order(order)

        order.assign(courier.id)
        await uow.order_repository.update_order(order)

    # Assert
    mock_event_publisher.publish.assert_called_once()
    published_events = mock_event_publisher.publish.call_args[0][0]
    assert len(published_events) == 2

    # Проверяем первое событие - создание заказа
    first_event = published_events[0]
    assert isinstance(first_event, OrderStatusChangedEvent)
    assert first_event.order_id == order_id
    assert first_event.order_status == OrderStatus.created()

    # Проверяем второе событие - назначение курьера
    second_event = published_events[1]
    assert isinstance(second_event, OrderStatusChangedEvent)
    assert second_event.order_id == order_id
    assert second_event.order_status == OrderStatus.assigned()
