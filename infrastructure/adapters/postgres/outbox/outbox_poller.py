import asyncio
import logging
from datetime import datetime

from sqlalchemy import select, update

from core.ports.event_publisher_interface import EventPublisherInterface
from infrastructure.adapters.postgres.outbox.models import OutboxEvent
from infrastructure.adapters.postgres.uow import UnitOfWork
from infrastructure.events.integration_event_registry import event_registry


class OutboxPollingPublisher:
    def __init__(
        self,
        uow: UnitOfWork,
        event_publisher: EventPublisherInterface,
        poll_interval: float = 0.3,
        batch_size: int = 100,
    ):
        self.uow = uow
        self.event_publisher = event_publisher
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self._is_running = False

    async def start(self):
        self._is_running = True
        while self._is_running:
            try:
                logging.info("[OutboxPoller] polling for events")
                await self._poll_once()
            except Exception as e:
                # log exception, backoff, etc.
                print(f"[OutboxPoller] error: {e}")
            await asyncio.sleep(self.poll_interval)

    async def stop(self):
        self._is_running = False

    async def _poll_once(self):
        async with self.uow:
            # SELECT ... FOR UPDATE SKIP LOCKED
            stmt = (
                select(OutboxEvent)
                .where(OutboxEvent.is_sent is False)
                .order_by(OutboxEvent.created_at)
                .limit(self.batch_size)
                .with_for_update(skip_locked=True)
            )

            result = await self.uow.session.execute(stmt)
            events = result.scalars().all()

            if not events:
                return

            domain_events = []

            for event in events:
                event_name = event.event_type
                integration_event = event_registry.get(event_name)
                if not integration_event:
                    raise ValueError(f"No integration event found for event {event.event_type}")

                integration_event_model, _ = integration_event["model"], integration_event["topic"]
                integration_event_data = integration_event_model.model_validate(event.payload, from_attributes=True)
                domain_events.append(integration_event_data)

            # Публикуем в брокер
            await self.event_publisher.publish(domain_events)

            # Обновляем is_sent
            ids = [e.id for e in events]
            await self.uow.session.execute(
                update(OutboxEvent).where(OutboxEvent.id.in_(ids)).values(is_sent=True, sent_at=datetime.utcnow())
            )

            await self.uow.commit()
            logging.info(f"[OutboxPoller] {len(events)} events published")
