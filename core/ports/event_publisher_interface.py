from abc import ABC, abstractmethod

from core.domain.events.base import BaseDomainEvent


class EventPublisherInterface(ABC):
    requires_commit_after_publish: bool

    @abstractmethod
    async def publish(self, events: list[BaseDomainEvent], *args, **kwargs):
        pass
