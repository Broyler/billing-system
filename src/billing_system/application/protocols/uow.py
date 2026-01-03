# src/billing_system/application/protocols/uow.py
from typing import Protocol

from billing_system.domain.repositories import InvoiceRepository


class UnitOfWork(Protocol):
    """Протокол unit of work (UOW)."""

    invoices: InvoiceRepository

    def commit(self) -> None:
        """Метод для сохранения изменений в репозиториях."""
        ...

    def rollback(self) -> None:
        """Метод для отката изменений в репозиториях."""
        ...

    def __enter__(self) -> "UnitOfWork":
        """Метод для входа в контекст UOW (with)."""
        ...

    def __exit__(self, *args: object) -> None:
        """Метод для выхода из контекста UOW."""
        ...
