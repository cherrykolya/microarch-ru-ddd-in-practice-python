from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class StoragePlace(BaseModel):
    id: UUID = Field(..., description="id места хранения")
    name: str
    total_volume: int
    order_id: UUID | None = None

    def can_store(self, volume: int) -> bool:
        if not isinstance(volume, int):
            raise ValueError("volume should be int")
        if self.order_id is not None:
            return False
        if volume > self.total_volume:
            return False
        return True

    def store(self, order_id: UUID, volume: int) -> bool:
        if not isinstance(order_id, UUID):
            raise ValueError("order_id should be UUID")
        if not self.can_store(volume):
            raise ValueError("Cannot store: either already occupied or volume too large")
        self.order_id = order_id
        return True

    def extract(self) -> UUID:
        if self.order_id is None:
            raise ValueError("StoragePlace is already empty")
        order_id = self.order_id
        self.order_id = None
        return order_id

    @classmethod
    def create_storage_place(cls, name: str, total_volume: int) -> "StoragePlace":
        if not isinstance(name, str):
            raise ValueError("name should be str")
        if not isinstance(total_volume, int):
            raise ValueError("total_volume should be int")
        if total_volume < 1:
            raise ValueError("total_volume should be more than 0")

        return cls(id=uuid4(), name=name, total_volume=total_volume)
