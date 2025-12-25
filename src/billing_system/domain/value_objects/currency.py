# src/billing_system/domain/value_objects/currency.py
# Value object для валюты
from enum import Enum

from billing_system.domain.errors import CurrencyMismatchError


class Currency(Enum):
    """Класс Enum для представления валюты. Имеет экспоненту."""

    RUB = "RUB"
    EUR = "EUR"
    USD = "USD"
    JPY = "JPY"

    @property
    def exp(self) -> int:
        """Метод-маппинг для получения экспоненты валюты (2 по умолчанию)."""
        return {
            Currency.RUB: 2,
            Currency.EUR: 2,
            Currency.USD: 2,
            Currency.JPY: 0,
        }.get(self, 2)

    @classmethod
    def from_code(cls, code: str) -> "Currency":
        """Метод для получения Enum валюты по значению."""
        try:
            return cls(code)
        except ValueError:
            msg = f"Нет такой валюты: {code}"
            raise CurrencyMismatchError(msg) from None
