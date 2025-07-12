import logging

from aiokafka import AIOKafkaProducer

from core.domain.events.base import BaseDomainEvent, OrderStatusChangedEvent
from core.ports.event_publisher_interface import EventPublisherInterface
from infrastructure.config.settings import get_settings

settings = get_settings()

domain_event_to_topic_mapping = {
    OrderStatusChangedEvent: settings.kafka.ORDER_STATUS_CHANGED_TOPIC,
}


class KafkaEventPublisher(EventPublisherInterface):
    def __init__(self, kafka_producer: AIOKafkaProducer):
        self.kafka_producer = kafka_producer

    async def publish(self, event: BaseDomainEvent):
        topic = domain_event_to_topic_mapping.get(type(event))
        if not topic:
            logging.error(f"No topic found for event {type(event)}")
            return

        await self.kafka_producer.send(topic, event.model_dump_json().encode("utf-8"))


def get_kafka_producer():
    return AIOKafkaProducer(
        bootstrap_servers="localhost:9092",
    )
