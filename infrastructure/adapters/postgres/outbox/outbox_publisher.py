from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.events.base import BaseDomainEvent
from core.ports.event_publisher_interface import EventPublisherInterface
from infrastructure.adapters.postgres.outbox.models import OutboxEvent


class OutboxPublisher(EventPublisherInterface):
    requires_commit_after_publish = True

    async def publish(self, events: list[BaseDomainEvent], session: AsyncSession):
        outbox_events = []
        for event in events:
            event_type = event.get_event_type()
            # Создаем словарь с данными вместо объекта
            outbox_events.append(
                {
                    "event_type": event_type,
                    "payload": event.model_dump(mode="json"),
                }
            )

        if outbox_events:
            query = insert(OutboxEvent).values(outbox_events)
            await session.execute(query)
