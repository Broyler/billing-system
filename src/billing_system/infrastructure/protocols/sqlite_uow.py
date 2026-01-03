# src/billing_system/infrastructure/protocols/sqlite_uow.py
import sqlite3
from pathlib import Path
from types import TracebackType

from billing_system.application.protocols import UnitOfWork
from billing_system.infrastructure.errors import (
    AlreadyInTransactionError,
    NoConnectionError,
)
from billing_system.infrastructure.repositories import InvoiceSqliteRepository


class SqliteUnitOfWork(UnitOfWork):
    """Класс UOW для Sqlite."""

    def __init__(self, path: Path) -> None:
        self.__path = path
        self.conn: sqlite3.Connection | None = None

    def __enter__(self) -> "SqliteUnitOfWork":
        if (
            isinstance(self.conn, sqlite3.Connection)
            and self.conn.in_transaction
        ):
            raise AlreadyInTransactionError
        self.conn = sqlite3.connect(self.__path)
        self.invoices = InvoiceSqliteRepository(self.conn)
        self.conn.cursor().execute("BEGIN;")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self.conn is None:
            return
        try:
            if exc_type is not None:
                if self.conn.in_transaction:
                    self.rollback()
            elif self.conn.in_transaction:
                self.commit()
        finally:
            self.conn.close()
            self.conn = None

    def commit(self) -> None:
        """Сохранение изменений в sqlite."""
        if self.conn is None:
            raise NoConnectionError(
                "Запуск commit() без with (вне контекста).",
            )
        self.conn.commit()

    def rollback(self) -> None:
        """Откат изменений в sqlite."""
        if self.conn is None:
            raise NoConnectionError(
                "Запуск rollback() без with (вне контекста).",
            )
        self.conn.rollback()
