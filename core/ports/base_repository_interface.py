from core.domain.events.base import BaseDomainEvent


class BaseRepository:
    def __init__(self):
        self.events: list[BaseDomainEvent] = []

    def register_event(self, event: BaseDomainEvent):
        self.events.append(event)

    def get_events(self) -> list[BaseDomainEvent]:
        events = self.events[:]
        self.clear_events()
        return events

    def clear_events(self):
        self.events.clear()
