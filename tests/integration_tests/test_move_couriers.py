from uuid import uuid4

import pytest

from core.application.use_cases.commands.move_couriers import MoveCouriersCommand
from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.model.order_aggregate.order_status import OrderStatus
from core.domain.shared_kernel.location import Location
from infrastructure.di.container import Container


@pytest.mark.asyncio
async def test_move_couriers_job(test_container: Container):
    uow = test_container.unit_of_work()
    move_couriers = test_container.move_couriers_use_case()

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
            location=Location.create(x=5, y=5),
            volume=1,
        )
        order.assign(courier.id)
        await uow.order_repository.add_order(order)
        await uow.commit()

    # Act
    await move_couriers.handle(MoveCouriersCommand())

    # Assert
    async with uow:
        # Check courier moved towards order
        updated_courier = await uow.courier_repository.get_courier(courier.id)
        assert updated_courier is not None

        # Courier should move towards order at (5,5)
        assert updated_courier.location.x > 1  # Moved right

        # Order should still be in progress
        updated_order = await uow.order_repository.get_order(order.id)
        assert updated_order is not None
        assert updated_order.order_status == OrderStatus.assigned()


@pytest.mark.asyncio
async def test_move_couriers_job_completes_order_when_arrived(test_container: Container):
    uow = test_container.unit_of_work()
    move_couriers = test_container.move_couriers_use_case()

    async with uow:
        # Create test courier at the order location
        location = Location.create(x=5, y=5)
        courier = Courier.create(
            name="Test Courier",
            speed=1,
            location=location,
        )
        await uow.courier_repository.add_courier(courier)

        # Create test order at the same location
        order = Order.create(
            order_id=uuid4(),
            location=location,
            volume=1,
        )
        await uow.order_repository.add_order(order)
        courier.take_order(order)
        await uow.courier_repository.update_courier(courier)
        await uow.order_repository.update_order(order)

        await uow.commit()

        # Act
        await move_couriers.handle(MoveCouriersCommand())

        # Order should be completed
        updated_order = await uow.order_repository.get_order(order.id)
        assert updated_order is not None
        assert updated_order.order_status == OrderStatus.completed()
