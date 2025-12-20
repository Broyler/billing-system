# src/billing_system/domain/value_objects/currency.py
# Value object для валюты
from enum import Enum


class Currency(Enum):
    """Класс Value Object для представления валюты."""

    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
