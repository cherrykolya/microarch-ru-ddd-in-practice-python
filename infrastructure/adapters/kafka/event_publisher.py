from aiokafka import AIOKafkaProducer

from core.domain.events.base import BaseDomainEvent
from core.ports.event_publisher_interface import EventPublisherInterface
from infrastructure.config.settings import get_settings
from infrastructure.events.integration_event_registry import event_registry

settings = get_settings()


class KafkaEventPublisher(EventPublisherInterface):
    requires_commit_after_publish = False

    def __init__(self, kafka_producer: AIOKafkaProducer):
        self.kafka_producer = kafka_producer

    async def publish(self, events: list[BaseDomainEvent]):
        for event in events:
            event_name = event.get_event_type()
            integration_event = event_registry.get(event_name)
            if not integration_event:
                raise ValueError(f"No integration event found for event {event.get_event_type()}")

            integration_event_model, topic = integration_event["model"], integration_event["topic"]
            integration_event_data = integration_event_model.model_validate(event, from_attributes=True)

            await self.kafka_producer.send(topic, integration_event_data.model_dump_json().encode("utf-8"))


def get_kafka_producer():
    return AIOKafkaProducer(
        bootstrap_servers="localhost:9092",
    )
