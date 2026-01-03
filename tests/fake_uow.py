# tests/fake_uow.py
from billing_system.application.protocols import UnitOfWork
from tests.invoice_in_memory import InvoiceRepoInMemo


class FakeUnitOfWork(UnitOfWork):
    """Класс UOW для тестирования, хранит данные в словаре."""

    def __init__(self) -> None:
        """Метод заглушка. Модуль для тестов. Не использовать."""
        self.invoices = InvoiceRepoInMemo()

    def commit(self) -> None:
        """Метод заглушка. Модуль для тестов. Не использовать."""

    def rollback(self) -> None:
        """Метод заглушка. Модуль для тестов. Не использовать."""

    def __enter__(self) -> UnitOfWork:
        """Метод заглушка. Модуль для тестов. Не использовать."""
        return self

    def __exit__(self, *args: object) -> None:
        """Метод заглушка. Модуль для тестов. Не использовать."""
