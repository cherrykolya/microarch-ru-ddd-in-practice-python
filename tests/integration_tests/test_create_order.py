from uuid import uuid4

import pytest

from core.application.use_cases.commands.create_order import CreateOrderCommand
from core.domain.model.order_aggregate.order_status import OrderStatusEnum
from infrastructure.di.container import Container


@pytest.mark.asyncio
async def test_create_order_persisted_to_database(test_container: Container):
    """Тест что созданный заказ сохраняется в базе данных."""
    # Arrange
    uow = test_container.unit_of_work()
    create_order_use_case = test_container.create_order_use_case()
    command = CreateOrderCommand(basket_id=uuid4(), street="Another Test Address", volume=25)

    # Act
    await create_order_use_case.handle(command)

    # Assert - проверяем что заказ сохранился в БД
    async with uow:
        saved_order = await uow.order_repository.get_one_created_order()
        assert saved_order is not None
        assert saved_order.volume == 25
        assert saved_order.order_status.name == OrderStatusEnum.CREATED
        assert saved_order.courier_id is None
