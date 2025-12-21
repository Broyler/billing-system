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
            raise InvalidMoneyError("Деньги должны быть вещественными.")

        q: Decimal = self.__quantize(self.amount)
        object.__setattr__(self, "amount", q)

    def __quantize(self, amount: Decimal) -> Decimal:
        """Квантование до точности валюты."""
        q_exp: Decimal = (
            Decimal("1." + "0" * self.currency.exp)
            if self.currency.exp > 0
            else Decimal(1)
        )
        return amount.quantize(q_exp, rounding=ROUND_HALF_UP)

    def __add__(self, other: object) -> "Money":
        """Сложение с другими деньгами."""
        if not isinstance(other, Money):
            raise TypeError("Можно складывать только деньги и деньги.")

        if self.currency != other.currency:
            raise CurrencyMismatchError("Можно складывать только одну валюту.")

        return Money(
            amount=self.amount + other.amount,
            currency=self.currency,
        )

    def __sub__(self, other: object) -> "Money":
        """Вычитание с другими деньгами."""
        if not isinstance(other, Money):
            raise TypeError("Можно вычитать только деньги и деньги.")

        if self.currency != other.currency:
            raise CurrencyMismatchError("Можно вычитать только одну валюту.")

        return Money(
            amount=self.amount - other.amount,
            currency=self.currency,
        )

    def __mul__(self, value: object) -> "Money":
        """Умножение денег на скаляр."""
        if not isinstance(value, (int, Decimal)):
            raise TypeError("Можно умножать деньги на int и Decimal.")

        value = Decimal(value)
        if not value.is_finite():
            raise InvalidMoneyError(
                "Деньги могут умножаться только на вещественное.",
            )

        return Money(
            amount=self.amount * value,
            currency=self.currency,
        )

    def __rmul__(self, value: object) -> "Money":
        """Поддержка умножения справа."""
        return self * value

    def __str__(self) -> str:
        """Получение строковых данных о деньгах."""
        return f"{self.amount} {self.currency.value}"
