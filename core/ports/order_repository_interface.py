from abc import ABC, abstractmethod
from uuid import UUID

from core.domain.model.order_aggregate.order_aggregate import Order


class OrderRepositoryInterface(ABC):
    @abstractmethod
    async def add_order(self, order: Order) -> Order:
        pass

    @abstractmethod
    async def update_order(self, order: Order) -> None:
        pass

    @abstractmethod
    async def get_order(self, order_id: UUID) -> Order | None:
        pass

    @abstractmethod
    async def get_one_created_order(self) -> Order | None:
        pass

    @abstractmethod
    async def get_all_assigned_orders(self) -> list[Order]:
        pass
