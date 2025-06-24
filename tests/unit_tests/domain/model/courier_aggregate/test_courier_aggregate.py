from uuid import uuid4

import pytest

from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.shared_kernel.location import Location


@pytest.fixture
def location() -> Location:
    return Location.create(1, 1)


@pytest.fixture
def courier(location) -> Courier:
    return Courier.create(name="John", speed=2, location=location)


def test_create_courier_success(location: Location):
    courier = Courier.create(name="Jane", speed=3, location=location)
    assert courier.name == "Jane"
    assert courier.speed == 3
    assert courier.location == location
    assert courier.storage_places is not None
    assert len(courier.storage_places) == 1


def test_create_courier_invalid_speed(location):
    with pytest.raises(ValueError, match="Speed must be greater than 0"):
        Courier.create(name="Jane", speed=0, location=location)


def test_add_storage_place(courier: Courier):
    courier.add_storage_place("trunk", 10)
    assert any(sp.name == "trunk" for sp in courier.storage_places)


def test_can_take_order_true(courier: Courier):
    order = Order.create(order_id=uuid4(), location=Location.create(5, 5), volume=1)
    assert courier.can_take_order(order) is True


def test_take_order_success(courier: Courier):
    order = Order.create(order_id=uuid4(), location=Location.create(5, 5), volume=1)
    courier.take_order(order)
    assert courier.get_storage_place_by_order_id(order.id) is not None
    assert order.courier_id == courier.id


def test_complete_order(courier: Courier):
    order = Order.create(order_id=uuid4(), location=Location.create(5, 5), volume=1)
    courier.take_order(order)
    courier.complete_order(order)
    assert order.order_status.name.value == "COMPLETED"
    with pytest.raises(ValueError):
        courier.get_storage_place_by_order_id(order.id)


def test_calculate_time_to_location(courier: Courier):
    location = Location.create(5, 5)
    time = courier.calculate_time_to_location(location)
    assert time == 4  # distance 8 / speed 2 = 4


def test_move_towards(courier: Courier):
    courier.move_towards(Location.create(5, 5))
    new_loc = courier.location
    assert new_loc.x > 1 or new_loc.y > 1
