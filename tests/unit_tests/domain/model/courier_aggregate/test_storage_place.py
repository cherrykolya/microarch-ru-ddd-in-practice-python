from uuid import uuid4

import pytest

from core.domain.model.courier_aggregate.storage_place import StoragePlace


def test_create_valid_storage_place():
    sp = StoragePlace.create_storage_place(name="рюкзак", total_volume=10)
    assert isinstance(sp, StoragePlace)
    assert sp.name == "рюкзак"
    assert sp.total_volume == 10
    assert sp.order_id is None


@pytest.mark.parametrize("invalid_name", [None, 123, 4.5])
def test_create_invalid_name(invalid_name):
    with pytest.raises(ValueError, match="name should be str"):
        StoragePlace.create_storage_place(name=invalid_name, total_volume=10)


@pytest.mark.parametrize("invalid_volume", [0, -5, "big"])
def test_create_invalid_total_volume(invalid_volume):
    with pytest.raises(ValueError):
        StoragePlace.create_storage_place(name="багажник", total_volume=invalid_volume)


def test_can_store_returns_true_when_valid():
    sp = StoragePlace.create_storage_place("рюкзак", 10)
    assert sp.can_store(5) is True


def test_can_store_returns_false_when_already_has_order():
    sp = StoragePlace.create_storage_place("рюкзак", 10)
    sp.order_id = uuid4()
    assert sp.can_store(5) is False


def test_can_store_returns_false_when_volume_too_large():
    sp = StoragePlace.create_storage_place("рюкзак", 10)
    assert sp.can_store(15) is False


def test_store_success():
    sp = StoragePlace.create_storage_place("рюкзак", 10)
    order_id = uuid4()
    result = sp.store(order_id=order_id, volume=5)
    assert result is True
    assert sp.order_id == order_id


def test_store_raises_when_order_id_invalid():
    sp = StoragePlace.create_storage_place("рюкзак", 10)
    with pytest.raises(ValueError, match="order_id should be UUID"):
        sp.store(order_id="not-uuid", volume=5)


def test_store_raises_when_volume_invalid():
    sp = StoragePlace.create_storage_place("рюкзак", 10)
    with pytest.raises(ValueError, match="volume should be int"):
        sp.can_store("a lot")  # использует внутри store


def test_store_raises_when_cannot_store():
    sp = StoragePlace.create_storage_place("рюкзак", 10)
    sp.order_id = uuid4()
    with pytest.raises(ValueError, match="Cannot store"):
        sp.store(order_id=uuid4(), volume=5)


def test_extract_success():
    sp = StoragePlace.create_storage_place("рюкзак", 10)
    order_id = uuid4()
    sp.store(order_id, volume=5)
    extracted_id = sp.extract()
    assert extracted_id == order_id
    assert sp.order_id is None


def test_extract_raises_when_empty():
    sp = StoragePlace.create_storage_place("рюкзак", 10)
    with pytest.raises(ValueError, match="StoragePlace is already empty"):
        sp.extract()
