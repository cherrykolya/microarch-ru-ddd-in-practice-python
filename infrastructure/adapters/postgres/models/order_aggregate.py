from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON
from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.model.order_aggregate.order_status import OrderStatusEnum
from infrastructure.adapters.postgres.models.base import Base


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID, primary_key=True)
    location: Mapped[dict] = mapped_column(JSON)
    volume: Mapped[int] = mapped_column(Integer)
    order_status: Mapped[str] = mapped_column(String(20))
    courier_id: Mapped[UUID | None] = mapped_column(ForeignKey("couriers.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    @classmethod
    def from_domain_object(cls, order: Order) -> "OrderModel":
        """Создать модель из доменного объекта."""
        return OrderModel(
            id=order.id,
            location=order.location.model_dump(),
            volume=order.volume,
            order_status=order.order_status.name,
            courier_id=order.courier_id,
        )

    def to_domain_object(self) -> Order:
        """Преобразовать модель в доменный объект."""
        order_status = OrderStatusEnum(self.order_status)
        return Order.model_validate({**self.__dict__, "order_status": order_status}, from_attributes=True)
