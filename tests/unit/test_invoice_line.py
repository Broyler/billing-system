# tests/unit/test_invoice_line.py
# Unit тесты для invoice line value object.
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from billing_system.domain.errors import (
    InvalidInvoiceLineError,
    InvalidQuantityError,
)
from billing_system.domain.value_objects import Currency, InvoiceLine, Money


def test_empty_description() -> None:
    with pytest.raises(InvalidInvoiceLineError):
        _ = InvoiceLine("    ", Money(Decimal(50), Currency.EUR), Decimal(20))

    with pytest.raises(InvalidInvoiceLineError):
        _ = InvoiceLine("", Money(Decimal(50), Currency.EUR), Decimal(20))


def test_long_description() -> None:
    with pytest.raises(InvalidInvoiceLineError):
        _ = InvoiceLine(
            "a" * 61,
            Money(Decimal(50), Currency.EUR),
            Decimal(20),
        )


def test_negative_quantity() -> None:
    with pytest.raises(InvalidQuantityError):
        _ = InvoiceLine(
            "Яблоко",
            Money(Decimal(50), Currency.EUR),
            Decimal(-1),
        )


def test_zero_quantity() -> None:
    with pytest.raises(InvalidQuantityError):
        _ = InvoiceLine(
            "Яблоко",
            Money(Decimal(50), Currency.EUR),
            Decimal(0),
        )


def test_str() -> None:
    line = InvoiceLine(
        "Фруктовая корзина",
        Money(Decimal(50), Currency.EUR),
        Decimal(20),
    )
    assert str(line) == "Фруктовая корзина: 20 * 50.00 EUR = 1000.00 EUR"


@given(
    st.decimals(
        allow_infinity=False,
        allow_nan=False,
        min_value=Decimal("-1e9"),
        max_value=Decimal("1e9"),
    ),
    st.decimals(
        allow_infinity=False,
        allow_nan=False,
        min_value=Decimal("1e-4"),
        max_value=Decimal("1e4"),
    ),
)
def test_correct_line_total(price: Decimal, count: Decimal) -> None:
    price_money = Money(price, Currency.EUR)
    line = InvoiceLine(
        "Яблоко",
        price_money,
        count,
    )
    assert line.line_total == price_money * count
