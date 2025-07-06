from abc import ABC, abstractmethod

from core.domain.shared_kernel.location import Location


class GeoServiceInterface(ABC):
    @abstractmethod
    async def get_location(self, street: str) -> Location:
        pass
