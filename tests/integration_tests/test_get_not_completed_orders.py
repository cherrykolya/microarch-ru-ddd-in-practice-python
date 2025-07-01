from uuid import uuid4

import pytest
from dependency_injector.providers import Resource
from sqlalchemy.ext.asyncio import AsyncSession

from core.application.use_cases.queries.get_not_completed_orders import (
    GetNotCompletedOrdersQuery,
    GetNotCompletedOrdersUseCase,
)
from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.shared_kernel.location import Location
from infrastructure.adapters.postgres.repositories.courier_repository import CourierRepository
from infrastructure.adapters.postgres.repositories.order_repository import OrderRepository
from infrastructure.di.container import Container


@pytest.mark.asyncio
async def test_get_not_completed_orders(db_session_with_commit: AsyncSession):
    # Создаем контейнер
    container = Container()

    # Переопределяем провайдер сессии, чтобы использовать сессию из фикстуры
    container.db_session.override(Resource(lambda: db_session_with_commit))

    container.init_resources()

    # Arrange
    repository: OrderRepository = await container.order_repository()

    courier_repository: CourierRepository = await container.courier_repository()
    courier = Courier.create(name="Test Courier", location=Location.create(x=1, y=1), speed=10)
    await courier_repository.add_courier(courier)

    # Создаем заказ со статусом CREATED
    location1 = Location.create(x=1, y=1)
    created_order = Order.create(order_id=uuid4(), location=location1, volume=100)
    await repository.add_order(created_order)

    # Создаем заказ со статусом ASSIGNED
    location2 = Location.create(x=2, y=2)
    assigned_order1 = Order.create(order_id=uuid4(), location=location2, volume=1)
    courier.take_order(assigned_order1)
    courier.complete_order(assigned_order1)
    await repository.add_order(assigned_order1)
    await courier_repository.update_courier(courier)

    # Получаем use case из контейнера
    get_not_completed_orders: GetNotCompletedOrdersUseCase = await container.get_not_completed_orders_use_case()

    # Используем use case
    result = await get_not_completed_orders.handle(GetNotCompletedOrdersQuery())

    assert result is not None
