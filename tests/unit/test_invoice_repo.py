# tests/unit/test_invoice_repo.py
from decimal import Decimal
from uuid import uuid4

import pytest

from billing_system.application.dto import (
    CreateInvoiceRequest,
    InvoiceAddLineRequest,
    IssueInvoiceRequest,
)
from billing_system.application.errors import InvoiceNotFoundError
from billing_system.application.usecase import (
    CreateInvoice,
    InvoiceAddLine,
    IssueInvoice,
)
from billing_system.domain.errors import (
    CurrencyMismatchError,
)
from billing_system.domain.value_objects import (
    Currency,
    InvoiceId,
    InvoiceStatus,
    Money,
)
from tests.fake_clock import FakeClock
from tests.fake_uow import FakeUnitOfWork


def test_create_invoice() -> None:
    uid = uuid4()
    req = CreateInvoiceRequest(id=uid, currency="EUR")
    uow = FakeUnitOfWork()
    CreateInvoice(uow)(req)
    invoice = uow.invoices.get(InvoiceId(uid))
    assert invoice.invoice_id == InvoiceId(uid)


def test_create_wrong_currency() -> None:
    uow = FakeUnitOfWork()
    uid = uuid4()
    with pytest.raises(CurrencyMismatchError):
        CreateInvoice(uow)(CreateInvoiceRequest(id=uid, currency="AAA"))


def test_add_line() -> None:
    uow = FakeUnitOfWork()
    uid = uuid4()
    CreateInvoice(uow)(CreateInvoiceRequest(id=uid, currency="EUR"))
    InvoiceAddLine(uow)(
        InvoiceAddLineRequest(
            invoice_id=uid,
            amount=Decimal("1.5"),
            quantity=Decimal("2.0"),
            description="Печенье",
        ),
    )
    invoice = uow.invoices.get(InvoiceId(uid))
    assert len(invoice.lines) == 1
    assert invoice.total == Money(Decimal("1.5"), Currency.EUR) * Decimal(
        "2.0",
    )
    assert invoice.status == InvoiceStatus.DRAFT


def test_issue_invoice() -> None:
    uow = FakeUnitOfWork()
    clock = FakeClock()
    uid = uuid4()
    CreateInvoice(uow)(CreateInvoiceRequest(id=uid, currency="EUR"))
    InvoiceAddLine(uow)(
        InvoiceAddLineRequest(
            invoice_id=uid,
            amount=Decimal("1.5"),
            quantity=Decimal("2.0"),
            description="Печенье",
        ),
    )
    IssueInvoice(uow, clock)(IssueInvoiceRequest(invoice_id=uid))
    invoice = uow.invoices.get(InvoiceId(uid))
    assert invoice.status == InvoiceStatus.ISSUED
    assert invoice.issued_at is not None


def test_find_non_existing_invoice() -> None:
    uow = FakeUnitOfWork()
    with pytest.raises(InvoiceNotFoundError):
        uow.invoices.get(InvoiceId(uuid4()))


def test_invoice_total_matches() -> None:
    uow = FakeUnitOfWork()
    clock = FakeClock()
    uid = uuid4()
    CreateInvoice(uow)(CreateInvoiceRequest(id=uid, currency="EUR"))
    InvoiceAddLine(uow)(
        InvoiceAddLineRequest(
            invoice_id=uid,
            amount=Decimal("1.5"),
            quantity=Decimal("2.0"),
            description="Печенье",
        ),
    )
    InvoiceAddLine(uow)(
        InvoiceAddLineRequest(
            invoice_id=uid,
            amount=Decimal("5.3"),
            quantity=Decimal("1.0"),
            description="Шоколад",
        ),
    )
    IssueInvoice(uow, clock)(IssueInvoiceRequest(invoice_id=uid))
    invoice = uow.invoices.get(InvoiceId(uid))
    mon1 = Money(Decimal("1.5"), Currency.EUR) * Decimal("2.0")
    mon2 = Money(Decimal("5.3"), Currency.EUR) * Decimal("1.0")
    assert invoice.total == mon1 + mon2
