import math
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from core.domain.consts import DEFAULT_BAG_NAME, DEFAULT_STORAGE_VOLUME
from core.domain.model.courier_aggregate.storage_place import StoragePlace
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.shared_kernel.location import Location


class Courier(BaseModel):
    id: UUID = Field(
        ...,
    )
    name: str = Field(..., description="")
    speed: int = Field(...)
    location: Location = Field()
    storage_places: list[StoragePlace] = Field()

    def __init__(self, **data):
        raise TypeError("Direct instantiation is not allowed. Use Courier.create()")

    @classmethod
    def create(cls, name: str, speed: int, location: Location) -> "Courier":
        if speed <= 0:
            raise ValueError("Speed must be greater than 0")

        return cls.model_construct(
            id=uuid4(),
            name=name,
            speed=speed,
            location=location,
            storage_places=[StoragePlace.create_storage_place(DEFAULT_BAG_NAME, DEFAULT_STORAGE_VOLUME)],
        )

    def add_storage_place(self, name: str, volume: int):
        storage_place = StoragePlace.create_storage_place(name, volume)
        self.storage_places.append(storage_place)

    def get_first_available_storage_place(self, volume: int) -> StoragePlace | None:
        for storage_place in self.storage_places:
            if storage_place.can_store(volume):
                return storage_place

        return None

    def get_storage_place_by_order_id(self, order_id: UUID) -> StoragePlace:
        for storage_place in self.storage_places:
            if storage_place.order_id == order_id:
                return storage_place

        raise ValueError(f"Where is no {order_id=} in courier storage places")

    def can_take_order(self, order: Order) -> bool:
        available_storage_place = self.get_first_available_storage_place(order.volume)
        return True if available_storage_place else False

    def take_order(self, order: Order):
        if not self.can_take_order(order):
            raise ValueError("Cant take order")

        storage_place = self.get_first_available_storage_place(order.volume)

        if storage_place is None:
            raise ValueError("Cant take order")

        storage_place.store(order.id, order.volume)

        # Нужно ли здесь проставлять id курьера в заказ?
        order.assign(self.id)

    def complete_order(self, order: Order):
        storage_place = self.get_storage_place_by_order_id(order.id)
        storage_place.extract()
        order.complete()

    def calculate_time_to_location(self, location: Location) -> int:
        distance = self.location.distance_to(location)
        return math.ceil(distance / self.speed)

    def move_towards(self, target: Location) -> None:
        if target is None:
            raise ValueError("Target location is required")

        dif_x = target.x - self.location.x
        dif_y = target.y - self.location.y
        cruising_range = self.speed

        move_x = max(-cruising_range, min(dif_x, cruising_range))
        cruising_range -= abs(move_x)

        move_y = max(-cruising_range, min(dif_y, cruising_range))

        try:
            new_location = Location.create(self.location.x + move_x, self.location.y + move_y)
        except ValueError as e:
            raise ValueError(f"Invalid new location: {e}")

        self.location = new_location
