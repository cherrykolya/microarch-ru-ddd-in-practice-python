from abc import ABC, abstractmethod


class BaseBackgroundJob(ABC):
    @abstractmethod
    async def execute(self):
        pass
