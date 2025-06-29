from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON
from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.courier_aggregate.storage_place import StoragePlace
from infrastructure.adapters.postgres.models.base import Base


class CourierModel(Base):
    __tablename__ = "couriers"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    speed: Mapped[int] = mapped_column(Integer)
    location: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    storage_places = relationship(
        "StoragePlaceModel",
        secondary="courier_storage_places",
        back_populates="couriers",
        lazy="joined",
        cascade="all, save-update",
    )

    @classmethod
    def from_domain_object(cls, courier: Courier) -> "CourierModel":
        """Создать модель из доменного объекта."""
        return CourierModel(
            id=courier.id,
            name=courier.name,
            speed=courier.speed,
            location=courier.location.model_dump(),
        )

    def to_domain_object(self) -> Courier:
        """Преобразовать модель в доменный объект."""
        return Courier.model_validate(self, from_attributes=True)


class CourierStoragePlaceModel(Base):
    """SQLAlchemy 2.0 модель для связи курьер-место хранения."""

    __tablename__ = "courier_storage_places"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID, primary_key=True)
    courier_id: Mapped[UUID] = mapped_column(ForeignKey("couriers.id"))
    storage_place_id: Mapped[UUID] = mapped_column(ForeignKey("storage_places.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class StoragePlaceModel(Base):
    """SQLAlchemy 2.0 модель для места хранения."""

    __tablename__ = "storage_places"

    id: Mapped[UUID] = mapped_column(SQLAlchemyUUID, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    total_volume: Mapped[int] = mapped_column(Integer)
    order_id: Mapped[UUID | None] = mapped_column(ForeignKey("orders.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    couriers = relationship("CourierModel", secondary="courier_storage_places", back_populates="storage_places")

    @classmethod
    def from_domain_object(cls, storage_place: StoragePlace) -> "StoragePlaceModel":
        """Создать модель из доменного объекта."""
        return StoragePlaceModel(
            id=storage_place.id,
            name=storage_place.name,
            total_volume=storage_place.total_volume,
            order_id=storage_place.order_id,
        )

    def to_domain_object(self) -> StoragePlace:
        """Преобразовать модель в доменный объект."""
        return StoragePlace.model_validate(self)
