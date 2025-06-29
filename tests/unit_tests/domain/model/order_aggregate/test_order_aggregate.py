from uuid import uuid4

import pytest

from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.model.order_aggregate.order_status import OrderStatus, OrderStatusEnum
from core.domain.shared_kernel.location import Location


@pytest.fixture
def location():
    return Location(x=5, y=5)


def test_create_order_success(default_location: Location, default_order_volume: int):
    order_id = uuid4()
    order = Order.create(order_id=order_id, location=default_location, volume=default_order_volume)

    assert order.id == order_id
    assert order.location == default_location
    assert order.volume == default_order_volume
    assert order.order_status.name == OrderStatusEnum.CREATED
    assert order.courier_id is None


def test_create_order_invalid_volume(default_location: Location):
    with pytest.raises(ValueError, match="Volume must be greater than 0"):
        Order.create(order_id=uuid4(), location=default_location, volume=0)


def test_assign_success(order: Order):
    courier_id = uuid4()
    order.assign(courier_id)

    assert order.courier_id == courier_id
    assert order.order_status.name == OrderStatusEnum.ASSIGNED


def test_assign_twice_raises(order: Order):
    courier_id = uuid4()
    order.assign(courier_id)

    with pytest.raises(ValueError, match="Courier already assigned"):
        order.assign(uuid4())


def test_complete_success(order: Order):
    order.assign(uuid4())
    order.complete()

    assert order.order_status.name == OrderStatusEnum.COMPLETED


def test_complete_without_assign_raises(order: Order):
    with pytest.raises(ValueError, match="Courier not assigned"):
        order.complete()


def test_complete_wrong_state_raises(order: Order):
    order.assign(uuid4())
    order.order_status = OrderStatus.created()  # симулируем сломанную логику

    with pytest.raises(ValueError, match="Order not in assigned state"):
        order.complete()
