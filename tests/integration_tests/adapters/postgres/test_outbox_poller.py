from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy import select

from core.domain.events.base import BaseDomainEvent, OrderStatusChangedEvent
from core.domain.model.order_aggregate.order_status import OrderStatus
from infrastructure.adapters.postgres.outbox.models import OutboxEvent
from infrastructure.adapters.postgres.outbox.outbox_poller import OutboxPollingPublisher
from infrastructure.adapters.postgres.outbox.outbox_publisher import OutboxPublisher
from infrastructure.di.container import Container
from infrastructure.events.integration_events import IntegrationOrderStatusChangedEvent


@pytest.fixture
def mock_event_publisher():
    mock = AsyncMock()
    return mock


@pytest.mark.asyncio
async def test_outbox_poller_publishes_events(test_container: Container, mock_event_publisher):
    # Arrange
    uow = test_container.unit_of_work()
    async with uow as uow:
        publisher = OutboxPublisher()
        order_id = uuid4()
        events: list[BaseDomainEvent] = [OrderStatusChangedEvent(order_id=order_id, order_status=OrderStatus.created())]

        # Act
        await publisher.publish(events, session=uow.session)

    async with uow as uow:
        poller = OutboxPollingPublisher(uow=uow, event_publisher=mock_event_publisher, poll_interval=0.1, batch_size=10)

        # Act
        await poller._poll_once()

        # Assert
        mock_event_publisher.publish.assert_called_once()
        published_events = mock_event_publisher.publish.call_args[0][0]
        assert len(published_events) == 1

        # Check published event
        event = published_events[0]
        assert isinstance(event, IntegrationOrderStatusChangedEvent)
        integration_event = cast(IntegrationOrderStatusChangedEvent, event)
        payload = OrderStatusChangedEvent.model_validate(integration_event.model_dump(), from_attributes=True)
        assert payload.order_id == order_id
        assert payload.order_status == OrderStatus.created()

        # Check that event was marked as sent
        result = await uow.session.execute(select(OutboxEvent))
        outbox_event = result.scalar_one()
        payload = OrderStatusChangedEvent.model_validate(outbox_event.payload, from_attributes=True)
        assert payload.order_id == order_id
        assert payload.order_status == OrderStatus.created()
        assert outbox_event.is_sent
        assert outbox_event.sent_at is not None


@pytest.mark.asyncio
async def test_outbox_poller_handles_unknown_event_type(test_container: Container, mock_event_publisher):
    # Arrange
    uow = test_container.unit_of_work()
    async with uow as uow:
        # Create an unknown event type
        unknown_event = BaseDomainEvent()
        publisher = OutboxPublisher()
        await publisher.publish([unknown_event], session=uow.session)

    async with uow as uow:
        poller = OutboxPollingPublisher(uow=uow, event_publisher=mock_event_publisher, poll_interval=0.1, batch_size=10)

        # Act & Assert
        with pytest.raises(ValueError, match="No integration event found for event"):
            await poller._poll_once()

        # Verify event publisher was not called
        mock_event_publisher.publish.assert_not_called()

        # Check that event was not marked as sent
        result = await uow.session.execute(select(OutboxEvent))
        outbox_event = result.scalar_one()
        assert not outbox_event.is_sent
        assert outbox_event.sent_at is None


@pytest.mark.asyncio
async def test_outbox_poller_processes_multiple_events(test_container: Container, mock_event_publisher):
    # Arrange
    uow = test_container.unit_of_work()
    async with uow as uow:
        publisher = OutboxPublisher()
        order_ids = [uuid4() for _ in range(3)]
        events: list[BaseDomainEvent] = [
            OrderStatusChangedEvent(order_id=order_id, order_status=OrderStatus.created()) for order_id in order_ids
        ]

        # Act
        await publisher.publish(events, session=uow.session)

    async with uow as uow:
        poller = OutboxPollingPublisher(uow=uow, event_publisher=mock_event_publisher, poll_interval=0.1, batch_size=10)

        # Act
        await poller._poll_once()

        # Assert
        mock_event_publisher.publish.assert_called_once()
        published_events = mock_event_publisher.publish.call_args[0][0]
        assert len(published_events) == 3

        # Check each published event
        for event, order_id in zip(published_events, order_ids):
            assert isinstance(event, IntegrationOrderStatusChangedEvent)
            integration_event = cast(IntegrationOrderStatusChangedEvent, event)
            payload = OrderStatusChangedEvent.model_validate(integration_event.model_dump(), from_attributes=True)
            assert payload.order_id == order_id
            assert payload.order_status == OrderStatus.created()

        # Check all events were marked as sent
        result = await uow.session.execute(select(OutboxEvent))
        outbox_events = result.scalars().all()

        assert len(outbox_events) == 3
        for event, order_id in zip(outbox_events, order_ids):
            payload = OrderStatusChangedEvent.model_validate(event.payload, from_attributes=True)
            assert payload.order_id == order_id
            assert payload.order_status == OrderStatus.created()
            assert event.is_sent
            assert event.sent_at is not None
