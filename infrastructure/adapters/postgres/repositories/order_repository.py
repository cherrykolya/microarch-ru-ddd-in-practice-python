from uuid import UUID

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.events.base import OrderStatusChangedEvent
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.model.order_aggregate.order_status import OrderStatusEnum
from core.ports.order_repository_interface import OrderRepositoryInterface
from infrastructure.adapters.postgres.models.order_aggregate import OrderModel


class OrderRepository(OrderRepositoryInterface):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def add_order(self, order: Order) -> Order:
        # Создаем заказ одним запросом
        order_values = {
            "id": order.id,
            "location": order.location.model_dump(),
            "volume": order.volume,
            "order_status": order.order_status.name,
            "courier_id": order.courier_id,
        }
        stmt = insert(OrderModel).values(order_values).returning(OrderModel)
        result = await self.session.execute(stmt)
        order_model = result.unique().scalar_one()
        self.register_event(OrderStatusChangedEvent(order_id=order.id, order_status=order.order_status))
        return order_model.to_domain_object()

    async def update_order(self, order: Order) -> None:
        # Получаем существующий заказ
        order_model = await self._get_order_model(order.id)
        if not order_model:
            raise ValueError(f"Order with id {order.id} not found")

        # Обновляем поля заказа
        order_model.location = order.location.model_dump()
        order_model.volume = order.volume
        order_model.order_status = order.order_status.name
        order_model.courier_id = order.courier_id

        await self.session.flush()
        self.register_event(OrderStatusChangedEvent(order_id=order.id, order_status=order.order_status))

    async def get_order(self, order_id: UUID) -> Order | None:
        order_model = await self._get_order_model(order_id)
        return order_model.to_domain_object() if order_model else None

    async def get_one_created_order(self) -> Order | None:
        query = (
            select(OrderModel)
            .filter(OrderModel.order_status == OrderStatusEnum.CREATED)
            .limit(1)
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(query)
        order_model = result.unique().scalar_one_or_none()
        return order_model.to_domain_object() if order_model else None

    async def get_all_assigned_orders(self) -> list[Order]:
        query = (
            select(OrderModel)
            .filter(OrderModel.order_status == OrderStatusEnum.ASSIGNED)
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(query)
        order_models = result.unique().scalars().all()
        return [order_model.to_domain_object() for order_model in order_models]

    async def _get_order_model(self, order_id: UUID) -> OrderModel | None:
        """Вспомогательный метод для получения модели заказа."""
        query = select(OrderModel).filter(OrderModel.id == order_id).execution_options(populate_existing=True)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()
