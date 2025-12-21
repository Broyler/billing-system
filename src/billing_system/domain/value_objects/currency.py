# src/billing_system/domain/value_objects/currency.py
# Value object для валюты
from enum import Enum


class Currency(Enum):
    """Класс Enum для представления валюты. Имеет экспоненту."""

    exp: int

    RUB = ("RUB", 2)
    EUR = ("EUR", 2)
    USD = ("USD", 2)
    JPY = ("JPY", 0)

    def __new__(cls, code: str, exp: int) -> "Currency":
        """Задает параметры кода и экспоненты валюты при создании."""
        obj = object.__new__(cls)
        obj._value_ = code
        obj.exp = exp
        return obj

    def __str__(self) -> str:
        return str(self.value)
