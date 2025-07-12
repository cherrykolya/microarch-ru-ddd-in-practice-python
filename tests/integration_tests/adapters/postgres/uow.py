import json
from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from core.domain.events.base import OrderStatusChangedEvent
from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.model.order_aggregate.order_status import OrderStatus
from core.domain.shared_kernel.location import Location
from infrastructure.di.container import Container


@pytest.mark.asyncio
async def test_uow_publishes_events_on_commit(test_container: Container):
    # Arrange
    order_id = uuid4()
    # Act
    async with test_container.unit_of_work() as uow:
        # Имитируем создание заказа, который должен опубликовать событие
        order = Order.create(order_id=order_id, location=Location.create(x=5, y=5), volume=1)
        await uow.order_repository.add_order(order)

    # Assert
    kafka_producer_mock = uow.event_publisher.kafka_producer.send
    assert kafka_producer_mock.call_count == 1
    call_args = kafka_producer_mock.call_args
    assert call_args is not None

    payload = json.loads(call_args[0][1])
    correct_payload = OrderStatusChangedEvent(order_id=order_id, order_status=OrderStatus.created()).model_dump_json()
    assert payload == json.loads(correct_payload)


@pytest.mark.asyncio
async def test_uow_does_not_publish_events_on_rollback(test_container: Container):
    # Arrange
    order_id = uuid4()

    # Act
    with pytest.raises(ValueError, match="Test exception"):
        async with test_container.unit_of_work() as uow:
            # Имитируем создание заказа, который должен вызвать ошибку
            order = Order.create(order_id=order_id, location=Location.create(x=5, y=5), volume=1)
            await uow.order_repository.add_order(order)
            raise ValueError("Test exception")

    # Assert
    mock_publish = cast(AsyncMock, uow.event_publisher.kafka_producer.send)
    assert mock_publish.call_count == 0


@pytest.mark.asyncio
async def test_uow_publishes_multiple_events_in_order(test_container: Container):
    # Arrange
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
    mock_publish = cast(AsyncMock, uow.event_publisher.kafka_producer.send)
    assert mock_publish.call_count == 2

    # Проверяем первое событие - создание заказа
    call_args_list = mock_publish.call_args_list
    assert len(call_args_list) >= 1
    first_event = call_args_list[0][0][1]
    payload = json.loads(first_event)
    correct_payload = OrderStatusChangedEvent(order_id=order_id, order_status=OrderStatus.created()).model_dump_json()
    assert payload == json.loads(correct_payload)

    # Проверяем второе событие - назначение курьера
    assert len(call_args_list) >= 2
    second_event = call_args_list[1][0][1]
    payload = json.loads(second_event)
    correct_payload = OrderStatusChangedEvent(order_id=order_id, order_status=OrderStatus.assigned()).model_dump_json()
    assert payload == json.loads(correct_payload)
