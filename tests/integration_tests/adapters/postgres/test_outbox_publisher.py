from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.events.base import BaseDomainEvent, OrderStatusChangedEvent
from core.domain.model.order_aggregate.order_status import OrderStatus
from infrastructure.adapters.postgres.outbox.models import OutboxEvent
from infrastructure.adapters.postgres.outbox.outbox_publisher import OutboxPublisher


@pytest.mark.asyncio
async def test_outbox_publisher_creates_event(db_session_with_commit: AsyncSession):
    # Arrange
    publisher = OutboxPublisher()
    order_id = uuid4()
    events: list[BaseDomainEvent] = [OrderStatusChangedEvent(order_id=order_id, order_status=OrderStatus.created())]

    # Act
    await publisher.publish(events, session=db_session_with_commit)

    # Assert
    stmt = select(OutboxEvent)
    result = await db_session_with_commit.execute(stmt)
    outbox_events = result.scalars().all()

    assert len(outbox_events) == 1
    outbox_event = outbox_events[0]
    assert outbox_event.event_type == "OrderStatusChangedEvent"
    payload = OrderStatusChangedEvent.model_validate(outbox_event.payload, from_attributes=True)
    assert payload.order_id == order_id
    assert payload.order_status == OrderStatus.created()
    assert not outbox_event.is_sent
    assert outbox_event.sent_at is None


@pytest.mark.asyncio
async def test_outbox_publisher_creates_multiple_events(db_session_with_commit: AsyncSession):
    # Arrange
    publisher = OutboxPublisher()
    order_id = uuid4()
    events: list[BaseDomainEvent] = [
        OrderStatusChangedEvent(order_id=order_id, order_status=OrderStatus.created()),
        OrderStatusChangedEvent(order_id=order_id, order_status=OrderStatus.assigned()),
    ]

    # Act
    await publisher.publish(events, db_session_with_commit)

    # Assert
    stmt = select(OutboxEvent).order_by(OutboxEvent.created_at)
    result = await db_session_with_commit.execute(stmt)
    outbox_events = result.scalars().all()

    assert len(outbox_events) == 2

    # Проверяем первое событие
    first_event = outbox_events[0]
    assert first_event.event_type == "OrderStatusChangedEvent"
    payload = OrderStatusChangedEvent.model_validate(first_event.payload, from_attributes=True)
    assert payload.order_id == order_id
    assert payload.order_status == OrderStatus.created()
    assert not first_event.is_sent
    assert first_event.sent_at is None

    # Проверяем второе событие
    second_event = outbox_events[1]
    assert second_event.event_type == "OrderStatusChangedEvent"
    payload = OrderStatusChangedEvent.model_validate(second_event.payload, from_attributes=True)
    assert payload.order_id == order_id
    assert payload.order_status == OrderStatus.assigned()
    assert not second_event.is_sent
    assert second_event.sent_at is None
