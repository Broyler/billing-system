# tests/unit/test_invoice_sql_repo.py
import datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from billing_system.application.dto import (
    CreateInvoiceRequest,
    InvoiceAddLineRequest,
)
from billing_system.application.dto.invoice import IssueInvoiceRequest
from billing_system.application.usecase import CreateInvoice, InvoiceAddLine
from billing_system.application.usecase.issue_invoice import IssueInvoice
from billing_system.domain.aggregates.invoice import Invoice
from billing_system.domain.errors.invoice_not_found import InvoiceNotFoundError
from billing_system.domain.errors.invoice_operation import (
    InvoiceOperationError,
)
from billing_system.domain.value_objects import (
    Currency,
    Discount,
    InvoiceId,
    InvoiceStatus,
    Money,
    Tax,
)
from billing_system.domain.value_objects.invoice_line import InvoiceLine
from billing_system.infrastructure.errors.no_connection import (
    NoConnectionError,
)
from billing_system.infrastructure.repositories import InvoiceSqliteRepository
from billing_system.infrastructure.repositories.invoice_sqlite_repo import (
    read_discount,
    read_tax,
)
from tests.fake_clock import FakeClock


def test_init(tmp_path: Path) -> None:
    f = tmp_path / "db.sqlite"
    InvoiceSqliteRepository(str(f))


def test_create_invoice(tmp_path: Path) -> None:
    f = tmp_path / "db.sqlite"
    repo = InvoiceSqliteRepository(str(f))
    uid = uuid4()
    cur = Currency.EUR.value
    with repo:
        CreateInvoice(repo)(CreateInvoiceRequest(id=uid, currency=cur))
        InvoiceAddLine(repo)(
            InvoiceAddLineRequest(
                invoice_id=uid,
                amount=Decimal("1.5"),
                quantity=Decimal("2.0"),
                description="Печенье",
            ),
        )
        invoice = repo.get(InvoiceId(uid))
        assert len(invoice.lines) == 1
        assert invoice.total == Money(Decimal("1.5"), Currency.EUR) * Decimal(
            "2.0",
        )
        assert invoice.status == InvoiceStatus.DRAFT


def test_issue_invoice(tmp_path: Path) -> None:
    f = tmp_path / "db.sqlite"
    repo = InvoiceSqliteRepository(str(f))
    uid = uuid4()
    clock = FakeClock()
    cur = Currency.EUR.value
    with repo:
        CreateInvoice(repo)(CreateInvoiceRequest(id=uid, currency=cur))
        InvoiceAddLine(repo)(
            InvoiceAddLineRequest(
                invoice_id=uid,
                amount=Decimal("1.5"),
                quantity=Decimal("2.0"),
                description="Печенье",
            ),
        )
        IssueInvoice(repo, clock)(IssueInvoiceRequest(invoice_id=uid))

    with repo:
        invoice = repo.get(InvoiceId(uid))
        assert invoice.status == InvoiceStatus.ISSUED
        assert invoice.issued_at == datetime.datetime(
            year=2020,
            month=11,
            day=1,
            tzinfo=datetime.UTC,
        )

        # Проверка инварианта на добавление строчек в выданный счет.
        with pytest.raises(InvoiceOperationError):
            invoice.add_line(
                InvoiceLine(
                    "Яблоко",
                    Money(Decimal("2.30"), Currency.EUR),
                    Decimal("1.0"),
                ),
            )


def test_read_tax() -> None:
    cur = Currency.EUR
    assert read_tax(None, cur) is None
    tax = Tax(Money(Decimal("15.36"), cur))
    assert read_tax(1536, cur) == tax


def test_read_discount() -> None:
    cur = Currency.EUR
    assert read_discount(None, cur) is None
    disc = Discount(Money(Decimal("43.552"), cur))
    assert read_discount(4355, cur) == disc


def test_no_cursor(tmp_path: Path) -> None:
    f = tmp_path / "db.sqlite"
    repo = InvoiceSqliteRepository(str(f))
    invoice = Invoice(Currency.EUR, InvoiceId(uuid4()))
    with pytest.raises(NoConnectionError):
        repo.add(invoice)


def test_invoice_not_found(tmp_path: Path) -> None:
    f = tmp_path / "db.sqlite"
    repo = InvoiceSqliteRepository(str(f))
    with pytest.raises(InvoiceNotFoundError), repo:
        repo.get(InvoiceId(uuid4()))
