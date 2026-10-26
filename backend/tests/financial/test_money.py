from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.accounting.money import money


@pytest.mark.parametrize(
    "value,currency",
    [
        ("NaN", "USD"),
        ("Infinity", "ZAR"),
        ("1.001", "USD"),
        (1.1, "USD"),
        ("10", "ZZZ"),
        ("1.1", "JPY"),
    ],
)
def test_invalid(value, currency):
    with pytest.raises(ValueError):
        money(value, currency)


@given(st.integers(min_value=0, max_value=10**10))
def test_cents_roundtrip(cents):
    amount = Decimal(cents) / 100
    assert money(str(amount), "ZAR") == amount
