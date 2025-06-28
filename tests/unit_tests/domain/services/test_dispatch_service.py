from uuid import uuid4

import pytest

from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.services.dispatch_service import Dispatcher
from core.domain.shared_kernel.location import Location


def test_dispatch_assigns_closest_courier(dispatcher: Dispatcher, courier: Courier, dispatch_order: Order):
    # Act
    assigned_courier = dispatcher.dispatch([courier], dispatch_order)

    # Assert
    assert assigned_courier.id == courier.id
    assert dispatch_order.courier_id == courier.id
    assert any(sp.order_id == dispatch_order.id for sp in assigned_courier.storage_places)


def test_dispatch_with_single_courier(dispatcher: Dispatcher, order: Order):
    # Arrange
    courier = Courier.create(name="Single Courier", speed=2, location=Location.create(1, 1))

    # Act
    assigned_courier = dispatcher.dispatch([courier], order)

    # Assert
    assert assigned_courier == courier
    assert order.courier_id == courier.id


def test_dispatch_with_full_storage_skips_courier(
    dispatcher: Dispatcher, courier: Courier, dispatch_order: Order, default_courier_speed: int
):
    # Arrange
    # Fill up the first courier's storage
    big_order = Order.create(order_id=uuid4(), location=Location.create(1, 1), volume=10)
    courier.take_order(big_order)

    # Create another courier that should take the order
    another_courier = Courier.create(
        name="Another Courier",
        speed=default_courier_speed,
        location=Location.create(3, 3),  # Дальше от заказа, чем первый курьер
    )

    # Act
    assigned_courier = dispatcher.dispatch([courier, another_courier], dispatch_order)

    # Assert
    assert assigned_courier.id == another_courier.id
    assert dispatch_order.courier_id == another_courier.id


def test_dispatch_with_no_couriers_raises(dispatcher: Dispatcher, dispatch_order: Order):
    # Act & Assert
    with pytest.raises(ValueError, match="No courier can take order"):
        dispatcher.dispatch([], dispatch_order)


def test_dispatch_with_all_couriers_full_raises(
    dispatcher: Dispatcher,
    courier: Courier,
    dispatch_order: Order,
    default_courier_speed: int,
    default_location: Location,
):
    # Arrange
    couriers = [courier, Courier.create(name="Courier 2", speed=default_courier_speed, location=default_location)]

    # Fill up all couriers
    big_order = Order.create(order_id=uuid4(), location=Location.create(1, 1), volume=10)
    for c in couriers:
        c.take_order(big_order.model_copy())

    # Act & Assert
    with pytest.raises(ValueError, match="No courier can take order"):
        dispatcher.dispatch(couriers, dispatch_order)


def test_dispatch_with_equal_distance_takes_first(
    dispatcher: Dispatcher, dispatch_order: Order, default_courier_speed: int
):
    # Arrange
    location = Location.create(5, 5)
    courier1 = Courier.create(name="Courier 1", speed=default_courier_speed, location=location)
    courier2 = Courier.create(name="Courier 2", speed=default_courier_speed, location=location)

    # Act
    assigned_courier = dispatcher.dispatch([courier1, courier2], dispatch_order)

    # Assert
    assert assigned_courier == courier1  # Should take the first one
    assert dispatch_order.courier_id == courier1.id
