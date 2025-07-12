from uuid import UUID

from pydantic import BaseModel, Field, model_serializer

from core.domain.model.order_aggregate.order_status import OrderStatus


class BaseDomainEvent(BaseModel):
    pass


class OrderStatusChangedEvent(BaseDomainEvent):
    order_id: UUID = Field(..., description="ID заказа")
    order_status: OrderStatus = Field(..., description="Статус заказа")

    @model_serializer()
    def serialize_model(self):
        return {
            "orderId": self.order_id,
            "orderStatus": self.order_status.name.value_number,
        }
