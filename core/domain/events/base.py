from uuid import UUID

from pydantic import BaseModel, Field

from core.domain.model.order_aggregate.order_status import OrderStatus


class BaseDomainEvent(BaseModel):
    @classmethod
    def get_event_type(cls) -> str:
        return cls.__name__


class OrderStatusChangedEvent(BaseDomainEvent):
    order_id: UUID = Field(..., description="ID заказа")
    order_status: OrderStatus = Field(..., description="Статус заказа")
