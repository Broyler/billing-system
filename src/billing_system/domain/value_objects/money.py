# src/billing_system/domain/value_objects/money.py
# Класс Value Object для представления денег
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from billing_system.domain.errors import (
    CurrencyMismatchError,
    InvalidMoneyError,
)

from .currency import Currency


@dataclass(frozen=True)
class Money:
    """Датакласс value object для представления денег в системе."""

    amount: Decimal
    currency: Currency

    def __post_init__(self) -> None:
        """Проверка инвариантов после инициализации."""
        if not self.amount.is_finite():
            raise InvalidMoneyError

        temp = self.amount.quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)
        object.__setattr__(self, "amount", temp)

    def __add__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            raise TypeError

        if self.currency != other.currency:
            # Инвариант: складывать можно только одну валюту
            raise CurrencyMismatchError

        return Money(
            amount=self.amount + other.amount,
            currency=self.currency,
        )

    def __sub__(self, other: object) -> "Money":
        if not isinstance(other, Money):
            raise TypeError

        if self.currency != other.currency:
            # Инвариант: вычитать можно только одну валюту
            raise CurrencyMismatchError

        return Money(
            amount=self.amount - other.amount,
            currency=self.currency,
        )

    def __mul__(self, value: object) -> "Money":
        if not isinstance(value, (int, Decimal)):
            raise TypeError

        value = Decimal(value)
        if not value.is_finite():
            # Инвариант: сумма должна быть числовой и конечной
            raise InvalidMoneyError

        return Money(
            amount=self.amount * Decimal(value),
            currency=self.currency,
        )

    def __str__(self) -> str:
        """Получение строковых данных о деньгах."""
        return f"{self.amount} {self.currency.value}"
