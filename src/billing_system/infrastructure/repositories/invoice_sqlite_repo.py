# src/billing_system/infrastructure/repositories/invoice_sqlite_repo.py
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from billing_system.domain.aggregates import Invoice, InvoiceRehydrateData
from billing_system.domain.errors import InvoiceNotFoundError
from billing_system.domain.repositories import InvoiceRepository
from billing_system.domain.value_objects import (
    Currency,
    Discount,
    InvoiceId,
    InvoiceLine,
    Money,
    Tax,
)
from billing_system.domain.value_objects.invoice_status import InvoiceStatus


def fromtimestamp(t: int | None) -> datetime | None:
    """Преобразовывает UNIX время в UTC datetime объект."""
    return datetime.fromtimestamp(t, tz=UTC) if t is not None else None


def dt_to_unix(dt: datetime | None) -> int | None:
    """Преобразовывает datetime объект в UNIX время для бд."""
    if not dt:
        return None
    return int(dt.timestamp())


def minor_to_money(amount_minor: int, currency: Currency) -> Money:
    """Преобразовывает минорную сумму в объект денег."""
    amount = Decimal(amount_minor) / 10**currency.exp
    return Money(amount=amount, currency=currency)


def money_to_minor(money: Money) -> int:
    """Преобразовывает объект денег в минорную сумму для бд."""
    return int(money.amount * 10**money.currency.exp)


def read_tax(amount: int | None, currency: Currency) -> Tax | None:
    """Собирает объект Tax из бд или возвращает None."""
    if amount is None:
        return None
    return Tax(minor_to_money(amount, currency))


def read_discount(amount: int | None, currency: Currency) -> Discount | None:
    """Собирает объект Discount из бд или возвращает None."""
    if amount is None:
        return None
    return Discount(minor_to_money(amount, currency))


@dataclass(frozen=True)
class InvoiceResultSQL:
    """Объект для преобразованных данных результатов запросов SQL."""

    id: InvoiceId
    currency: Currency
    status: InvoiceStatus
    tax: Tax | None
    discount: Discount | None
    iss_at: datetime | None
    paid_at: datetime | None
    voided_at: datetime | None
    paid_idempotency: str | None
    voided_idempotency: str | None


class InvoiceSqliteRepository(InvoiceRepository):
    """Класс репозитория счета с sqlite3."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.__conn = conn
        self.__create_tables()

    @property
    def __cursor(self) -> sqlite3.Cursor:
        return self.__conn.cursor()

    def __create_tables(self) -> None:
        """Метод должен создать таблицы на старте репозитория."""
        queries = [
            """
            PRAGMA foreign_keys = ON;
            """,
            """
            CREATE TABLE IF NOT EXISTS `Invoice`
            (
                id TEXT PRIMARY KEY,
                currency TEXT NOT NULL,
                status TEXT NOT NULL,
                tax_amount_minor INTEGER,
                discount_amount_minor INTEGER,
                issued_at INTEGER,
                paid_at INTEGER,
                voided_at INTEGER,
                payment_idempotency_key TEXT,
                void_idempotency_key TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS `InvoiceLine`
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT NOT NULL,
                description TEXT,
                unit_price_minor INTEGER NOT NULL,
                quantity TEXT NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES Invoice(id)
            );
            """,
        ]
        for q in queries:
            self.__cursor.execute(q)

    def __get_invoice_data(self, invoice_id: InvoiceId) -> InvoiceResultSQL:
        """Метод возвращает сырые данные счета по Id."""
        _id = str(invoice_id)
        q = """
        SELECT * FROM `Invoice`
        WHERE `id` = ?
        LIMIT 1;
        """
        res = self.__cursor.execute(q, (_id,))
        i = res.fetchone()
        if not i:
            raise InvoiceNotFoundError("Счет не найден.")
        currency = Currency(i[1])
        return InvoiceResultSQL(
            id=InvoiceId(i[0]),
            currency=currency,
            status=InvoiceStatus(i[2]),
            tax=read_tax(i[3], currency),
            discount=read_discount(i[4], currency),
            iss_at=fromtimestamp(i[5]),
            paid_at=fromtimestamp(i[6]),
            voided_at=fromtimestamp(i[7]),
            paid_idempotency=i[8],
            voided_idempotency=i[9],
        )

    def __get_invoice(
        self,
        data: InvoiceResultSQL,
        lines: list[InvoiceLine],
    ) -> Invoice:
        """Метод возвращает базовый объект счета по его данным."""
        return Invoice.rehydrate(
            InvoiceRehydrateData(
                invoice_id=data.id,
                currency=data.currency,
                status=data.status,
                issued_at=data.iss_at,
                paid_at=data.paid_at,
                voided_at=data.voided_at,
                lines=lines,
                tax=data.tax,
                discount=data.discount,
                paid_idempotency=data.paid_idempotency,
                void_idempotency=data.voided_idempotency,
            ),
        )

    def __get_invoice_lines(
        self,
        invoice_id: InvoiceId,
        invoice_currency: Currency,
    ) -> list[InvoiceLine]:
        """Метод возвращает список строчек счета по его Id и валюте."""
        _id = str(invoice_id)
        cur = self.__cursor
        q = """
        SELECT * FROM `InvoiceLine`
        WHERE `invoice_id` = ?;
        """
        res = cur.execute(q, (_id,))
        lines = res.fetchall()
        return [
            InvoiceLine(
                description=line[2],
                unit_price=minor_to_money(line[3], invoice_currency),
                quantity=Decimal(line[4]),
            )
            for line in lines
        ]

    def __delete_old_invoice_lines(self, invoice: Invoice) -> None:
        """Метод для удаления старых строчек счета."""
        q = """
        DELETE FROM `InvoiceLine` WHERE
        `invoice_id` = ?;
        """
        self.__cursor.execute(q, (str(invoice.invoice_id),))

    def __create_new_invoice_lines(self, invoice: Invoice) -> None:
        """Метод для создания новых строчек счета."""
        q = """
        INSERT INTO `InvoiceLine` (invoice_id, description,
        unit_price_minor, quantity) VALUES (?, ?, ?, ?);
        """
        cur = self.__cursor
        for line in invoice.lines:
            cur.execute(
                q,
                (
                    str(invoice.invoice_id),
                    line.description,
                    money_to_minor(line.unit_price),
                    str(line.quantity),
                ),
            )

    def __update_invoice_lines(self, invoice: Invoice) -> None:
        """Метод для обновления строчек счета на записи."""
        self.__delete_old_invoice_lines(invoice)
        self.__create_new_invoice_lines(invoice)

    def get(self, invoice_id: InvoiceId) -> Invoice:
        """Метод должен возвращать счет по его Id."""
        invoice_data = self.__get_invoice_data(invoice_id)
        lines = self.__get_invoice_lines(invoice_id, invoice_data.currency)
        return self.__get_invoice(invoice_data, lines=lines)

    def add(self, invoice: Invoice) -> None:
        """Создает счет в БД."""
        q = """
        INSERT INTO `Invoice` (id, currency, status, tax_amount_minor,
        discount_amount_minor, issued_at, paid_at, voided_at,
        payment_idempotency_key, void_idempotency_key) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        );
        """
        self.__cursor.execute(
            q,
            (
                str(invoice.invoice_id),
                invoice.currency.value,
                invoice.status.value,
                money_to_minor(invoice.tax.amount)
                if isinstance(invoice.tax, Tax)
                else None,
                money_to_minor(invoice.discount.amount)
                if isinstance(invoice.discount, Discount)
                else None,
                dt_to_unix(invoice.issued_at),
                dt_to_unix(invoice.paid_at),
                dt_to_unix(invoice.voided_at),
                invoice.payment_idempotency_key,
                invoice.void_idempotency_key,
            ),
        )
        self.__update_invoice_lines(invoice)

    def save(self, invoice: Invoice) -> None:
        """Обновляет объект счета в БД."""
        q = """
        UPDATE `Invoice` SET currency = ?, status = ?, tax_amount_minor = ?,
        discount_amount_minor = ?, issued_at = ?, paid_at = ?, voided_at = ?,
        payment_idempotency_key = ?, void_idempotency_key = ?
        WHERE id = ?;
        """
        self.__cursor.execute(
            q,
            (
                invoice.currency.value,
                invoice.status.value,
                money_to_minor(invoice.tax.amount)
                if isinstance(invoice.tax, Tax)
                else None,
                money_to_minor(invoice.discount.amount)
                if isinstance(invoice.discount, Discount)
                else None,
                dt_to_unix(invoice.issued_at),
                dt_to_unix(invoice.paid_at),
                dt_to_unix(invoice.voided_at),
                invoice.payment_idempotency_key,
                invoice.void_idempotency_key,
                str(invoice.invoice_id),
            ),
        )
        self.__update_invoice_lines(invoice)
