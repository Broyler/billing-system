# src/billing_system/domain/value_objects/invoice_line.py
# Класс Value Object для записи в счете.
from dataclasses import dataclass
from decimal import Decimal

from billing_system.domain.errors import (
    InvalidInvoiceLineError,
    InvalidQuantityError,
)

from .money import Money

MAX_LINE_DESCRIPTION_LENGTH = 60


@dataclass(frozen=True)
class InvoiceLine:
    """Класс данных Value Object для строчки/записи в счете."""

    description: str
    unit_price: Money
    quantity: Decimal  # Может быть вещественным для граммовок

    def __post_init__(self) -> None:
        if not self.description.strip():
            raise InvalidInvoiceLineError("Нужно описание для строчки счета.")
        if len(self.description.strip()) > MAX_LINE_DESCRIPTION_LENGTH:
            msg = (
                f"Описание строчки не может быть длиннее"
                f"{MAX_LINE_DESCRIPTION_LENGTH} символов.",
            )
            raise InvalidInvoiceLineError(msg)
        if self.quantity <= 0:
            raise InvalidQuantityError("Количество должно быть положительным.")

    @property
    def line_total(self) -> Money:
        """Свойство для получения общей суммы за строчку."""
        return self.unit_price * self.quantity

    def __str__(self) -> str:
        """Магический метод для представления строчки счета как строки."""
        return (
            f"{self.description}: {self.quantity} * "
            f"{self.unit_price} = {self.line_total}"
        )
