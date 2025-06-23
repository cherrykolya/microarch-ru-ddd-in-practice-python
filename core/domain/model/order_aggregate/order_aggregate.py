from uuid import UUID

from pydantic import BaseModel, Field

from core.domain.model.order_aggregate.order_status import OrderStatus
from core.domain.shared_kernel.location import Location


class Order(BaseModel):
    id: UUID = Field(..., description="The unique identifier for the order.")
    location: Location = Field(..., description="The location where the order is being placed.")
    volume: int = Field(..., description="The volume of the order.")
    order_status: OrderStatus | None = Field(None, description="The status of the order.")
    courier_id: UUID | None = Field(None, description="The ID of the courier assigned to the order.")

    def __init__(self, **data):
        raise TypeError("Direct instantiation is not allowed. Use Order.create()")

    @classmethod
    def create(cls, order_id: UUID, location: Location, volume: int) -> "Order":
        if volume <= 0:
            raise ValueError("Volume must be greater than 0")

        return cls.model_construct(
            id=order_id,
            location=location,
            volume=volume,
            order_status=OrderStatus.created(),
            courier_id=None,
        )

    def assign(self, courier_id: UUID):
        if self.courier_id:
            raise ValueError("Courier already assigned to order.")

        self.courier_id = courier_id
        self.order_status = OrderStatus.assigned()

        return

    def complete(self):
        if self.courier_id is None:
            raise ValueError("Courier not assigned to order.")

        if self.order_status != OrderStatus.assigned():
            raise ValueError("Order not in assigned state.")

        self.order_status = OrderStatus.completed()

        return
