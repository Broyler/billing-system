# tests/unit/test_money.py
# Unit тесты для VO Money типа денег
from decimal import ROUND_HALF_UP, Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from billing_system.domain.errors import (
    CurrencyMismatchError,
    InvalidMoneyError,
)
from billing_system.domain.value_objects import (
    Currency,
    Money,
)


@pytest.mark.parametrize(
    "mon1, mon2, eq",
    [
        (
            Money(amount=Decimal(50), currency=Currency.EUR),
            Money(amount=Decimal(50), currency=Currency.EUR),
            True,
        ),
        (
            Money(amount=Decimal(36), currency=Currency.RUB),
            Money(amount=Decimal("36.00"), currency=Currency.RUB),
            True,
        ),
        (
            Money(amount=Decimal(36), currency=Currency.RUB),
            Money(amount=Decimal(54), currency=Currency.RUB),
            False,
        ),
        (
            Money(amount=Decimal(36), currency=Currency.USD),
            Money(amount=Decimal("36.01"), currency=Currency.USD),
            False,
        ),
        (
            Money(amount=Decimal("36.01"), currency=Currency.EUR),
            Money(amount=Decimal("36.01"), currency=Currency.USD),
            False,
        ),
    ],
)
def test_equals_same_cur(mon1: Money, mon2: Money, eq: bool) -> None:
    if eq:
        assert mon1 == mon2

    else:
        assert mon1 != mon2


@pytest.mark.parametrize(
    "mon, val, op_minus",
    [
        (Money(Decimal("36.00"), Currency.RUB), 50, False),
        (Money(Decimal("36.00"), Currency.RUB), Decimal("60.0"), False),
        (Money(Decimal("36.00"), Currency.RUB), "hello", False),
        (Money(Decimal("36.00"), Currency.RUB), 50, True),
        (Money(Decimal("36.00"), Currency.RUB), Decimal("60.0"), True),
        (Money(Decimal("36.00"), Currency.RUB), "hello", True),
    ],
)
def test_wrong_types(mon: Money, val: object, op_minus: bool) -> None:
    if op_minus:
        with pytest.raises(TypeError):
            _ = mon - val
    else:
        with pytest.raises(TypeError):
            _ = mon + val


def test_right_types() -> None:
    mon1 = Money(Decimal("36.00"), Currency.USD)
    assert mon1 * 10 == mon1 * Decimal("10.00")

    mon1 = Money(Decimal("36.00"), Currency.USD)
    mon2 = mon1 * 10
    assert mon2.amount == Decimal("360.00")

    mon1 = Money(Decimal("36.00"), Currency.USD)
    assert mon1 * 20 != mon1 * Decimal(10)

    mon1 = Money(Decimal("36.00"), Currency.USD)
    mon2 = Money(Decimal(20), Currency.USD)
    assert (mon1 + mon2).amount == Decimal("56.00")

    mon1 = Money(Decimal("36.00"), Currency.USD)
    mon2 = Money(Decimal(20), Currency.USD)
    assert (mon1 - mon2).amount == Decimal("16.00")


@pytest.mark.parametrize(
    "mon1, mon2, minus_op",
    [
        (
            Money(Decimal("50.00"), Currency.USD),
            Money(Decimal("25.00"), Currency.EUR),
            True,
        ),
        (
            Money(Decimal("50.00"), Currency.USD),
            Money(Decimal("25.00"), Currency.EUR),
            False,
        ),
    ],
)
def test_currency_mismatch(mon1: Money, mon2: Money, minus_op: bool) -> None:
    if minus_op:
        with pytest.raises(CurrencyMismatchError):
            _ = mon1 - mon2

    else:
        with pytest.raises(CurrencyMismatchError):
            _ = mon1 + mon2


def test_finite_on_init() -> None:
    with pytest.raises(InvalidMoneyError):
        Money(Decimal("inf"), Currency.USD)

    with pytest.raises(InvalidMoneyError):
        Money(Decimal("-inf"), Currency.USD)

    with pytest.raises(InvalidMoneyError):
        Money(Decimal("NaN"), Currency.USD)


def test_negative_money() -> None:
    mon1 = Money(Decimal("-40.00"), currency=Currency.RUB)
    assert mon1.amount == Decimal("-40.00")

    mon1 = Money(Decimal(500), Currency.USD)
    assert (mon1 * -3).amount == Decimal("-1500.00")


def test_decimal_mult() -> None:
    mon1 = Money(Decimal("10.00"), Currency.RUB)
    mon2 = mon1 * Decimal("0.333")
    assert mon2.amount == Decimal("3.33")

    mon1 = Money(Decimal(50), Currency.JPY)
    mon2 = mon1 * Decimal("0.33")
    assert mon2.amount == Decimal(17)


@pytest.mark.parametrize(
    "val",
    [
        Decimal("NaN"),
        Decimal("inf"),
        Decimal("-inf"),
    ],
)
def test_invalid_mul(val: Decimal) -> None:
    mon1 = Money(Decimal(500), Currency.USD)
    with pytest.raises(InvalidMoneyError):
        _ = mon1 * val


@given(
    st.decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=Decimal("-1e9"),
        max_value=Decimal("1e9"),
        places=2,
    ),
    st.decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=Decimal("-1e9"),
        max_value=Decimal("1e9"),
        places=2,
    ),
)
def test_addition(x: Decimal, y: Decimal) -> None:
    cur = Currency.EUR
    mon1 = Money(x, currency=cur)
    mon2 = Money(y, currency=cur)
    result = (mon1 + mon2).amount
    dec_q = Decimal(1) if cur.exp == 0 else Decimal(f"1.{'0' * cur.exp}")
    q1 = x.quantize(dec_q, ROUND_HALF_UP)
    q2 = y.quantize(dec_q, ROUND_HALF_UP)
    s = q1 + q2
    assert s == result
    assert result.as_tuple().exponent == -cur.exp


@given(
    st.decimals(
        allow_infinity=False,
        allow_nan=False,
        min_value=Decimal("-1e9"),
        max_value=Decimal("1e9"),
    ),
    st.integers(min_value=0, max_value=1),
)
def test_money_accepts_less_places(d: Decimal, places: int) -> None:
    q_exp: Decimal = Decimal("1." + "0" * places) if places > 0 else Decimal(1)
    dec = d.quantize(q_exp, ROUND_HALF_UP)
    # Деньги могут быть менее точными, чем их валюта.
    mon = Money(dec, Currency.EUR)
    assert mon.amount.as_tuple().exponent == -Currency.EUR.exp
    assert mon.amount == dec.quantize(q_exp)
