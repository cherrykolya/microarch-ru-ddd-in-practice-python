from uuid import uuid4

import pytest

from core.application.use_cases.queries.get_not_completed_orders import GetNotCompletedOrdersQuery
from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.shared_kernel.location import Location
from infrastructure.di.container import Container


@pytest.mark.asyncio
async def test_get_not_completed_orders(test_container: Container):
    uow = test_container.unit_of_work()
    get_not_completed_orders = test_container.get_not_completed_orders_use_case()

    async with uow:
        # Create test courier
        courier = Courier.create(
            name="Test Courier",
            speed=10,
            location=Location.create(x=1, y=1),
        )
        await uow.courier_repository.add_courier(courier)

        # Create order with CREATED status
        created_order = Order.create(
            order_id=uuid4(),
            location=Location.create(x=1, y=1),
            volume=100,
        )
        await uow.order_repository.add_order(created_order)

        # Create order with COMPLETED status
        completed_order = Order.create(
            order_id=uuid4(),
            location=Location.create(x=2, y=2),
            volume=1,
        )
        courier.take_order(completed_order)
        courier.complete_order(completed_order)
        await uow.order_repository.add_order(completed_order)
        await uow.courier_repository.update_courier(courier)
        await uow.commit()

    # Act
    result = await get_not_completed_orders.handle(GetNotCompletedOrdersQuery())

    # Assert
    assert result is not None
    assert len(result) == 1
    assert result[0].id == created_order.id
