from abc import ABC, abstractmethod


class Query(ABC):
    pass


class QueryHandler(ABC):
    @abstractmethod
    async def handle(self, query: Query) -> None:
        pass
