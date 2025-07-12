from uuid import uuid4

import pytest

from core.domain.model.courier_aggregate.courier_aggregate import Courier
from core.domain.model.order_aggregate.order_aggregate import Order
from core.domain.services.dispatch_service import Dispatcher
from core.domain.shared_kernel.location import Location

# TODO: при расширении доменной модели и увеличении фикстур можно делить по доменам


@pytest.fixture
def default_location() -> Location:
    """Базовая локация для тестов."""
    return Location.create(1, 1)


@pytest.fixture
def default_courier_speed() -> int:
    """Базовая скорость курьера для тестов."""
    return 2


@pytest.fixture
def default_order_volume() -> int:
    """Базовый объем заказа для тестов."""
    return 5


@pytest.fixture
def courier(default_location, default_courier_speed) -> Courier:
    """Базовый курьер для тестов."""
    return Courier.create(name="Test Courier", speed=default_courier_speed, location=default_location)


@pytest.fixture
def order(default_location, default_order_volume) -> Order:
    """Базовый заказ для тестов."""
    return Order.create(order_id=uuid4(), location=default_location, volume=default_order_volume)


@pytest.fixture
def dispatcher() -> Dispatcher:
    """Диспетчер для тестов."""
    return Dispatcher()


@pytest.fixture
def couriers(courier_locations) -> list[Courier]:
    return [Courier.create(name=f"Courier {i}", speed=2, location=loc) for i, loc in enumerate(courier_locations, 1)]


@pytest.fixture
def courier_locations() -> list[Location]:
    return [
        Location.create(1, 1),  # closest
        Location.create(10, 10),  # furthest
        Location.create(5, 5),  # middle
    ]


@pytest.fixture
def order_location() -> Location:
    """Локация заказа для тестов диспетчера."""
    return Location.create(2, 2)


@pytest.fixture(autouse=False)
def dispatch_order(order_location: Location, default_order_volume: int) -> Order:
    """Заказ для тестов диспетчера с особой локацией."""
    return Order.create(order_id=uuid4(), location=order_location, volume=default_order_volume)
