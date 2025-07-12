from dependency_injector.wiring import Provide, inject

from core.ports.event_publisher_interface import EventPublisherInterface
from infrastructure.adapters.postgres.outbox.outbox_poller import OutboxPollingPublisher
from infrastructure.adapters.postgres.uow import UnitOfWork
from infrastructure.di.container import Container


@inject
async def run_outbox_poller(
    uow: UnitOfWork = Provide[Container.unit_of_work],
    event_publisher: EventPublisherInterface = Provide[Container.kafka_event_publisher],
):
    outbox_poller = OutboxPollingPublisher(uow=uow, event_publisher=event_publisher)
    await outbox_poller.start()
