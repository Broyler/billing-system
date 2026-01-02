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
from billing_system.domain.errors.invoice_operation import (
    InvoiceOperationError,
)
from billing_system.domain.value_objects import (
    Currency,
    InvoiceId,
    InvoiceStatus,
    Money,
)
from billing_system.domain.value_objects.invoice_line import InvoiceLine
from billing_system.infrastructure.repositories import InvoiceSqliteRepository
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
