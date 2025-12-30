# tests/invoice_in_memory.py
from billing_system.application.errors import InvoiceNotFoundError
from billing_system.domain.aggregates import Invoice
from billing_system.domain.repositories import InvoiceRepository
from billing_system.domain.value_objects import InvoiceId


class InvoiceRepoInMemo(InvoiceRepository):
    """Класс репозитория счетов хранимый в памяти."""

    def __init__(self) -> None:
        self.__data: dict[InvoiceId, Invoice] = {}

    def save(self, invoice: Invoice) -> None:
        """Сохраняет счет в локальном словаре в памяти."""
        self.__data[invoice.invoice_id] = invoice

    def get(self, invoice_id: InvoiceId) -> Invoice:
        """Возвращает сохраненный счет или ошибку InvoiceNotFoundError."""
        if invoice_id not in self.__data:
            msg = f"Счет с id={invoice_id} не найден."
            raise InvoiceNotFoundError(msg)
        return self.__data[invoice_id]

    def add(self, invoice: Invoice) -> None:
        """Создает счет в памяти (словарь)."""
        self.__data[invoice.invoice_id] = invoice
