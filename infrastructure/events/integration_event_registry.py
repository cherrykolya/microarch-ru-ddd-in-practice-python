from typing import Dict, Type

from core.domain.events.base import BaseDomainEvent

# Глобальный реестр событий
event_registry: Dict[str, dict] = {}


def register_event(*, topic: str):
    """
    Декоратор для регистрации события.
    Используется в инфраструктуре, применим в домене.
    """

    def decorator(cls: Type[BaseDomainEvent]):
        event_type = cls.get_event_type()
        event_registry[event_type] = {
            "model": cls,
            "topic": topic,
        }
        return cls

    return decorator
