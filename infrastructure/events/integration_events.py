from pydantic import ConfigDict

from core.domain.events.base import OrderStatusChangedEvent
from infrastructure.config.settings import get_settings
from infrastructure.events.integration_event_registry import register_event

settings = get_settings()


def to_camel(string: str) -> str:
    parts = string.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


@register_event(topic=settings.kafka.ORDER_STATUS_CHANGED_TOPIC)
class IntegrationOrderStatusChangedEvent(OrderStatusChangedEvent):
    @classmethod
    def get_event_type(cls) -> str:
        return "OrderStatusChangedEvent"

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
