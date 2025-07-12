from abc import ABC, abstractmethod

from core.domain.events.base import BaseDomainEvent


class EventPublisherInterface(ABC):
    @abstractmethod
    async def publish(self, event: BaseDomainEvent):
        pass
