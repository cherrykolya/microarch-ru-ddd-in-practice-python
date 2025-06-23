import pytest
from pydantic import ValidationError

from core.domain.model.order_aggregate.order_status import OrderStatus, OrderStatusEnum


def test_create_from_enum():
    status = OrderStatus(name=OrderStatusEnum.CREATED)
    assert isinstance(status.name, OrderStatusEnum)
    assert status.name == OrderStatusEnum.CREATED
    assert status.name.value == "CREATED"


def test_create_from_str():
    status = OrderStatus(name="ASSIGNED")
    assert isinstance(status.name, OrderStatusEnum)
    assert status.name == OrderStatusEnum.ASSIGNED


@pytest.mark.parametrize("invalid_input", ["NEW", "", None, 123])
def test_invalid_value_raises_validation_error(invalid_input):
    with pytest.raises(ValidationError):
        OrderStatus(name=invalid_input)


def test_named_constructors_still_work():
    assert OrderStatus.created().name == OrderStatusEnum.CREATED
    assert OrderStatus.assigned().name == OrderStatusEnum.ASSIGNED
    assert OrderStatus.completed().name == OrderStatusEnum.COMPLETED


def test_value_object_equality():
    status1 = OrderStatus(name="COMPLETED")
    status2 = OrderStatus(name=OrderStatusEnum.COMPLETED)
    assert status1 == status2


def test_order_status_is_immutable():
    status = OrderStatus(name="CREATED")
    with pytest.raises(ValidationError):
        status.name = OrderStatusEnum.ASSIGNED
