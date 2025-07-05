from uuid import uuid4

import pytest

from core.application.use_cases.commands.assign_orders import AssignOrdersCommand
from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.model.order_aggregate.order_status import OrderStatus
from core.domain.shared_kernel.location import Location
from infrastructure.di.container import Container


@pytest.mark.asyncio
async def test_assign_orders_job(test_container: Container):
    uow = test_container.unit_of_work()
    assign_orders = test_container.assign_orders_use_case()

    async with uow:
        # Create test courier
        courier = Courier.create(
            name="Test Courier",
            speed=1,
            location=Location.create(x=1, y=1),
        )
        await uow.courier_repository.add_courier(courier)

        # Create test order
        order = Order.create(
            order_id=uuid4(),
            location=Location.create(x=2, y=2),
            volume=1,
        )
        await uow.order_repository.add_order(order)
        await uow.commit()

    # Act
    await assign_orders.handle(AssignOrdersCommand())

    # Assert
    async with uow:
        # Order should be assigned to courier
        updated_order = await uow.order_repository.get_order(order.id)
        assert updated_order is not None
        assert updated_order.order_status == OrderStatus.assigned()
        assert updated_order.courier_id == courier.id

        # Courier should have order in storage
        updated_courier = await uow.courier_repository.get_courier(courier.id)
        assert updated_courier is not None
        assert updated_courier.get_storage_place_by_order_id(order.id) is not None


@pytest.mark.asyncio
async def test_assign_orders_job_skips_busy_courier(test_container: Container):
    uow = test_container.unit_of_work()
    assign_orders = test_container.assign_orders_use_case()

    async with uow:
        # Create test courier with existing order
        courier = Courier.create(
            name="Test Courier",
            speed=1,
            location=Location.create(x=1, y=1),
        )
        await uow.courier_repository.add_courier(courier)

        existing_order = Order.create(
            order_id=uuid4(),
            location=Location.create(x=2, y=2),
            volume=1,
        )
        await uow.order_repository.add_order(existing_order)
        courier.take_order(existing_order)

        await uow.courier_repository.update_courier(courier)
        await uow.order_repository.update_order(existing_order)

        # Create new order
        new_order = Order.create(
            order_id=uuid4(),
            location=Location.create(x=3, y=3),
            volume=1,
        )
        await uow.order_repository.add_order(new_order)
        await uow.commit()

    # Act
    await assign_orders.handle(AssignOrdersCommand())

    # Assert
    async with uow:
        # New order should still be unassigned
        updated_order = await uow.order_repository.get_order(new_order.id)
        assert updated_order is not None
        assert updated_order.order_status == OrderStatus.created()
        assert updated_order.courier_id is None
