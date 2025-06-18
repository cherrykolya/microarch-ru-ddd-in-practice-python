import pytest
from pydantic import ValidationError
from returns.result import Failure, Success

from core.domain.shared_kernel.location import Location  # Замени на путь к твоей модели


def test_create_valid_location():
    result = Location.create(3, 4)
    assert isinstance(result, Success)

    loc = result.unwrap()
    assert loc.x == 3
    assert loc.y == 4


def test_create_invalid_x():
    result = Location.create(0, 5)
    assert isinstance(result, Failure)
    assert result.failure() == "Invalid x-coordinate"

    result = Location.create(11, 5)
    assert isinstance(result, Failure)
    assert result.failure() == "Invalid x-coordinate"


def test_create_invalid_y():
    result = Location.create(5, 0)
    assert isinstance(result, Failure)
    assert result.failure() == "Invalid y-coordinate"

    result = Location.create(5, 11)
    assert isinstance(result, Failure)
    assert result.failure() == "Invalid y-coordinate"


def test_distance_to():
    loc1 = Location.create(1, 2).unwrap()
    loc2 = Location.create(4, 5).unwrap()
    assert loc1.distance_to(loc2) == 6  # |1-4| + |2-5| = 3 + 3


def test_location_equality_and_hash():
    loc1 = Location.create(5, 5).unwrap()
    loc2 = Location.create(5, 5).unwrap()
    loc3 = Location.create(6, 5).unwrap()

    assert loc1 == loc2
    assert loc1 != loc3

    loc_set = {loc1, loc2, loc3}
    assert len(loc_set) == 2


def test_create_random():
    loc = Location.create_random()
    assert isinstance(loc, Location)
    assert 1 <= loc.x <= 10
    assert 1 <= loc.y <= 10


def test_unable_to_set_x_y_after_creation():
    loc = Location.create_random()
    with pytest.raises(ValidationError):
        loc.x = 100
    with pytest.raises(ValidationError):
        loc.y = 100
