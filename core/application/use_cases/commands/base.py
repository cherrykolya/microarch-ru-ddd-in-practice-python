from abc import ABC, abstractmethod

from pydantic import BaseModel


class Command(BaseModel):
    pass


class CommandHandler(ABC):
    @abstractmethod
    async def handle(self, command: Command) -> None:
        pass
