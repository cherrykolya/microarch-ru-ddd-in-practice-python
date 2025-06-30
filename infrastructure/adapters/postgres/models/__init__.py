"""
Этот модуль импортирует все модели SQLAlchemy, чтобы они были доступны для Alembic.
Важно импортировать здесь все модели, чтобы они были зарегистрированы в metadata.
"""

from infrastructure.adapters.postgres.models.base import Base
from infrastructure.adapters.postgres.models.courier_aggregate import CourierModel, StoragePlaceModel
from infrastructure.adapters.postgres.models.order_aggregate import OrderModel

__all__ = [
    "Base",
    "CourierModel",
    "StoragePlaceModel",
    "OrderModel",
]
