import pytest

from app.database import get_user_by_id
from app.services import calculate_discount, format_user_data


def test_calculate_discount_valid():
    assert calculate_discount(100.0, 20.0) == 80.0
    assert calculate_discount(50.0, 0.0) == 50.0
    assert calculate_discount(50.0, 100.0) == 0.0


def test_calculate_discount_invalid():
    with pytest.raises(ValueError):
        calculate_discount(100.0, -1.0)
    with pytest.raises(ValueError):
        calculate_discount(100.0, 101.0)


def test_get_user_by_id_and_format():
    row = get_user_by_id("1")
    assert format_user_data(row) == {"id": "1", "name": "Alice"}


def test_calculate_discount_failing():
    # Intentionally incorrect expectation: 20% off 100.0 is 80.0, not 85.0.
    assert calculate_discount(100.0, 20.0) == 85.0
