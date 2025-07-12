from enum import Enum

from pydantic import BaseModel, Field


class OrderStatusEnum(str, Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"

    @property
    def value_number(self) -> int:
        # Порядковый номер начинается с 1
        return list(OrderStatusEnum).index(self) + 1


class OrderStatus(BaseModel):
    name: OrderStatusEnum = Field(..., description="Имя статуса заказа")

    model_config = {"frozen": True}

    @classmethod
    def created(cls) -> "OrderStatus":
        return cls(name=OrderStatusEnum.CREATED)

    @classmethod
    def assigned(cls) -> "OrderStatus":
        return cls(name=OrderStatusEnum.ASSIGNED)

    @classmethod
    def completed(cls) -> "OrderStatus":
        return cls(name=OrderStatusEnum.COMPLETED)
