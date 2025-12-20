# tests/unit/test_money.py
# Unit тесты для VO Money типа денег
import unittest
from decimal import Decimal

import pytest

from billing_system.domain.value_objects import Currency, Money


class TestMoneyEquals(unittest.TestCase):
    def test_equals_same_currency(self) -> None:
        mon1 = Money(amount=Decimal(50), currency=Currency.EUR)
        mon2 = Money(amount=Decimal(50), currency=Currency.EUR)
        assert mon1 == mon2

        mon1 = Money(amount=Decimal(36), currency=Currency.EUR)
        mon2 = Money(amount=Decimal(54), currency=Currency.EUR)
        assert mon1 != mon2

        mon1 = Money(amount=Decimal("36.01"), currency=Currency.EUR)
        mon2 = Money(amount=Decimal(36), currency=Currency.EUR)
        assert mon1 != mon2

        mon1 = Money(amount=Decimal(36), currency=Currency.EUR)
        mon2 = Money(amount=Decimal("36.00"), currency=Currency.EUR)
        mon3 = Money(amount=Decimal(36), currency=Currency.EUR)
        assert mon1 == mon2 == mon3

    def test_equals_diff_currency(self) -> None:
        mon1 = Money(amount=Decimal(50), currency=Currency.RUB)
        mon2 = Money(amount=Decimal(50), currency=Currency.EUR)
        assert mon1 != mon2

        mon1 = Money(amount=Decimal(36), currency=Currency.USD)
        mon2 = Money(amount=Decimal(54), currency=Currency.RUB)
        assert mon1 != mon2

        mon1 = Money(amount=Decimal("36.01"), currency=Currency.RUB)
        mon2 = Money(amount=Decimal(36), currency=Currency.USD)
        assert mon1 != mon2

        mon1 = Money(amount=Decimal(36), currency=Currency.RUB)
        mon2 = Money(amount=Decimal("36.00"), currency=Currency.USD)
        mon3 = Money(amount=Decimal(36), currency=Currency.EUR)
        assert mon1 != mon2 != mon3

    def test_wrong_types(self) -> None:
        with pytest.raises(TypeError) as _:
            mon1 = Money(amount=Decimal("36.00"), currency=Currency.USD)
            mon1 + 50
