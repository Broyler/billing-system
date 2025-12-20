# src/billing_system/domain/value_objects/discount.py
# Класс Value Object для скидки
from dataclasses import dataclass

from .money import Money


@dataclass(frozen=True)
class Discount:
    """Класс Value Object для скидки.

    В будущем может быть как и процентом, так и количеством денег,
    с помощью Value Object типа DiscountType.
    """

    amount: Money

    def __str__(self) -> str:
        """Магический метод для представления скидки в виде строки."""
        return str(self.amount)
