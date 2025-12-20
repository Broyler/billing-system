# src/billing_system/domain/value_objects/tax.py
# Класс Value Object для представления налога

from dataclasses import dataclass

from .money import Money


@dataclass(frozen=True)
class Tax:
    """Класс Value Object для налога.

    Пока что представлен в виде кол-ва денег.
    Может быть расширен с помощью VO типа TaxType/TaxMode.
    """

    amount: Money
