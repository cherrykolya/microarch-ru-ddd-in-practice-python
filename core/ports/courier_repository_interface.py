from abc import ABC, abstractmethod
from uuid import UUID

from core.domain.model.courier_aggregate.courier_aggregate import Courier


class CourierRepositoryInterface(ABC):
    @abstractmethod
    async def add_courier(self, courier: Courier) -> Courier:
        pass

    @abstractmethod
    async def update_courier(self, courier: Courier) -> None:
        pass

    @abstractmethod
    async def get_courier(self, courier_id: UUID) -> Courier | None:
        pass

    @abstractmethod
    async def get_all_free_couriers(self) -> list[Courier]:
        pass
