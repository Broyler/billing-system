# src/billing_system/domain/repositories/invoice.py
from abc import ABC, abstractmethod

from billing_system.domain.aggregates import Invoice
from billing_system.domain.value_objects import InvoiceId


class InvoiceRepository(ABC):
    """Абстрактный класс репозитория счета."""

    @abstractmethod
    def get(self, invoice_id: InvoiceId) -> Invoice:
        """Метод должен возвращать счет по его Id."""

    @abstractmethod
    def add(self, invoice: Invoice) -> None:
        """Метод должен создавать счет."""

    @abstractmethod
    def save(self, invoice: Invoice) -> None:
        """Метод должен обновлять существующий счет."""
