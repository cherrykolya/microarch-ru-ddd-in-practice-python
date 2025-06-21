import pytest
from pydantic import ValidationError

from core.domain.shared_kernel.location import Location


def test_create_valid_location():
    loc = Location.create(3, 4)
    assert isinstance(loc, Location)
    assert loc.x == 3
    assert loc.y == 4


@pytest.mark.parametrize("x", [0, 11])
def test_create_invalid_x(x):
    with pytest.raises(ValueError, match="Invalid x-coordinate"):
        Location.create(x, 5)


@pytest.mark.parametrize("y", [0, 11])
def test_create_invalid_y(y):
    with pytest.raises(ValueError, match="Invalid y-coordinate"):
        Location.create(5, y)


def test_distance_to():
    loc1 = Location.create(1, 2)
    loc2 = Location.create(4, 5)
    assert loc1.distance_to(loc2) == 6  # |1-4| + |2-5| = 3 + 3


def test_location_equality_and_hash():
    loc1 = Location.create(5, 5)
    loc2 = Location.create(5, 5)
    loc3 = Location.create(6, 5)

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
