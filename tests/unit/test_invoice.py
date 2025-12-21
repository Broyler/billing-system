# tests/unit/test_invoice.py
import secrets
import uuid
from decimal import Decimal

import pytest

from billing_system.domain.aggregates import Invoice
from billing_system.domain.errors import (
    InvoiceCurrencyMismatchError,
    InvoiceOperationError,
    NegativeMoneyError,
)
from billing_system.domain.value_objects import (
    Currency,
    Discount,
    InvoiceId,
    InvoiceLine,
    InvoiceStatus,
    Money,
    Tax,
)
from tests.fake_clock import FakeClock


def test_invoice_init() -> None:
    invoice_draft = Invoice(Currency.RUB, InvoiceId(uuid.uuid4()))
    assert invoice_draft.status == InvoiceStatus.DRAFT
    assert invoice_draft.total.amount == Decimal("0.00")
    assert invoice_draft.total.currency == Currency.RUB
    assert invoice_draft.currency == Currency.RUB
    assert len(invoice_draft.lines) == 0


def test_invoice_mutability_draft() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    assert len(invoice_draft.lines) == 1
    assert invoice_draft.total == Money(Decimal("1.29"), Currency.EUR) * 4
    invoice_draft.add_line(
        InvoiceLine(
            "Cherry",
            Money(Decimal("10.99"), Currency.EUR),
            Decimal("1.530"),  # в граммах
        ),
    )
    assert len(invoice_draft.lines) == 1 + 1
    assert invoice_draft.total == Money(
        Decimal("1.29") * 4,
        Currency.EUR,
    ) + Money(Decimal("10.99"), Currency.EUR) * Decimal("1.530")


def test_invoice_discount() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    invoice_draft.set_discount(Discount(Money(Decimal("0.39"), Currency.EUR)))
    assert invoice_draft.total == Money(
        Decimal("1.29") * 4 - Decimal("0.39"),
        Currency.EUR,
    )


def test_invoice_tax() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    invoice_draft.set_tax(Tax(Money(Decimal("1.2"), Currency.EUR)))
    assert invoice_draft.total == Money(
        Decimal("1.29"),
        Currency.EUR,
    ) * 4 + Money(
        Decimal("1.2"),
        Currency.EUR,
    )


def test_invoice_discount_and_tax() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    invoice_draft.set_discount(Discount(Money(Decimal("0.39"), Currency.EUR)))
    invoice_draft.set_tax(Tax(Money(Decimal("1.2"), Currency.EUR)))
    assert invoice_draft.total == Money(
        Decimal("1.29"),
        Currency.EUR,
    ) * 4 + Money(Decimal("1.2"), Currency.EUR) - Money(
        Decimal("0.39"),
        Currency.EUR,
    )
    assert invoice_draft.subtotal == Money(Decimal("1.29"), Currency.EUR) * 4


def test_add_different_currency() -> None:
    invoice_draft = Invoice(Currency.USD, InvoiceId(uuid.uuid4()))
    invoice_line = InvoiceLine(
        "Banana",
        Money(Decimal("1.29"), Currency.EUR),
        Decimal(4),
    )
    with pytest.raises(InvoiceCurrencyMismatchError):
        invoice_draft.add_line(invoice_line)


def test_immutable_after_draft() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    clock = FakeClock()
    invoice_draft.issue(clock)
    assert invoice_draft.status == InvoiceStatus.ISSUED
    assert invoice_draft.issued_at is not None

    # Попытка добавить строку в созданный счет
    with pytest.raises(InvoiceOperationError):
        invoice_draft.add_line(
            InvoiceLine(
                "Pineapple",
                Money(Decimal("4.2"), Currency.EUR),
                Decimal(4),
            ),
        )

    # Попытка создать счет еще раз
    with pytest.raises(InvoiceOperationError):
        invoice_draft.issue(clock)

    assert isinstance(invoice_draft.lines, tuple)
    lines = list(invoice_draft.lines)
    lines.append(
        InvoiceLine(
            "Pineapple",
            Money(Decimal("4.2"), Currency.EUR),
            Decimal(4),
        ),
    )

    assert len(invoice_draft.lines) == 1


def test_immutable_tax_discount() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    tax = Tax(Money(Decimal("0.2"), Currency.EUR))
    invoice_draft.set_tax(tax)
    clock = FakeClock()
    invoice_draft.issue(clock)

    with pytest.raises(InvoiceOperationError):
        invoice_draft.set_tax(Tax(Money(Decimal("0.4"), Currency.EUR)))

    assert invoice_draft.tax == tax

    with pytest.raises(InvoiceOperationError):
        invoice_draft.set_discount(
            Discount(Money(Decimal("1.2"), Currency.EUR)),
        )

    assert invoice_draft.discount is None


def test_empty_issue() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    clock = FakeClock()
    with pytest.raises(InvoiceOperationError):
        invoice_draft.issue(clock)


def test_negative_total() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    invoice_draft.set_discount(
        Discount(Money(Decimal("100.00"), Currency.EUR)),
    )
    with pytest.raises(NegativeMoneyError):
        _ = invoice_draft.total


def test_void_init() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    clock = FakeClock()
    invoice_draft.void(clock, secrets.token_urlsafe(16))
    assert invoice_draft.status == InvoiceStatus.VOID
    assert invoice_draft.voided_at is not None


def test_void_immut() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    clock = FakeClock()
    invoice_draft.void(clock, secrets.token_urlsafe(16))

    # Попытка добавить строчку (нельзя)
    with pytest.raises(InvoiceOperationError):
        invoice_draft.add_line(
            InvoiceLine(
                "Banana",
                Money(Decimal("1.29"), Currency.EUR),
                Decimal(4),
            ),
        )

    assert len(invoice_draft.lines) == 1

    # Попытка установить скидку
    with pytest.raises(InvoiceOperationError):
        invoice_draft.set_discount(
            Discount(Money(Decimal("1.00"), Currency.EUR)),
        )

    # Попытка установить налог
    with pytest.raises(InvoiceOperationError):
        invoice_draft.set_tax(Tax(Money(Decimal("1.00"), Currency.EUR)))


def test_void_switch_state() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    clock = FakeClock()
    invoice_draft.void(clock, secrets.token_urlsafe(16))
    with pytest.raises(InvoiceOperationError):
        invoice_draft.issue(clock)

    with pytest.raises(InvoiceOperationError):
        invoice_draft.mark_paid(clock, secrets.token_urlsafe(16))


def test_void_after_issue() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    clock = FakeClock()
    invoice_draft.issue(clock)
    invoice_draft.void(clock, secrets.token_urlsafe(16))
    assert invoice_draft.status == InvoiceStatus.VOID
    assert invoice_draft.issued_at is not None  # Храним для аудита
    assert invoice_draft.voided_at is not None


def test_draft_illegal_states() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    clock = FakeClock()
    with pytest.raises(InvoiceOperationError):
        invoice_draft.mark_paid(clock, secrets.token_urlsafe(16))


def test_pay() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    clock = FakeClock()
    invoice_draft.issue(clock)
    invoice_draft.mark_paid(clock, secrets.token_urlsafe(16))
    assert invoice_draft.status == InvoiceStatus.PAID
    assert invoice_draft.paid_at is not None


def test_pay_illegal_states() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    clock = FakeClock()
    invoice_draft.issue(clock)
    invoice_draft.mark_paid(clock, secrets.token_urlsafe(16))

    with pytest.raises(InvoiceOperationError):
        invoice_draft.void(clock, secrets.token_urlsafe(16))

    with pytest.raises(InvoiceOperationError):
        invoice_draft.issue(clock)


def test_empty_void_idempotency_key() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    clock = FakeClock()
    with pytest.raises(InvoiceOperationError):
        invoice_draft.void(clock, "    ")


def test_void_paid_invoice() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    clock = FakeClock()
    invoice_draft.issue(clock)
    invoice_draft.mark_paid(clock, secrets.token_urlsafe(16))

    with pytest.raises(InvoiceOperationError):
        invoice_draft.void(clock, secrets.token_urlsafe(16))


def test_empty_payment_idempotency_key() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    clock = FakeClock()
    invoice_draft.issue(clock)
    with pytest.raises(InvoiceOperationError):
        invoice_draft.mark_paid(clock, "    ")


def test_tax_currency_mismatch() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    with pytest.raises(InvoiceCurrencyMismatchError):
        invoice_draft.set_tax(Tax(Money(Decimal("1.01"), Currency.RUB)))


def test_discount_currency_mismatch() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    with pytest.raises(InvoiceCurrencyMismatchError):
        invoice_draft.set_discount(
            Discount(Money(Decimal("1.01"), Currency.RUB)),
        )


def test_void_idempotency() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    clock = FakeClock()
    idempotency_key = secrets.token_urlsafe(16)
    invoice_draft.void(clock, idempotency_key)
    first_void = invoice_draft.voided_at
    invoice_draft.void(clock, idempotency_key)
    assert invoice_draft.voided_at == first_void
    assert invoice_draft.status == InvoiceStatus.VOID

    # Попытка использования другого ключа (другое аннулирование)
    with pytest.raises(InvoiceOperationError):
        invoice_draft.void(clock, "123")


def test_payment_idempotency() -> None:
    invoice_draft = Invoice(Currency.EUR, InvoiceId(uuid.uuid4()))
    invoice_draft.add_line(
        InvoiceLine(
            "Banana",
            Money(Decimal("1.29"), Currency.EUR),
            Decimal(4),
        ),
    )
    clock = FakeClock()
    idempotency_key = secrets.token_urlsafe(16)
    invoice_draft.issue(clock)
    invoice_draft.mark_paid(clock, idempotency_key)
    first_paid = invoice_draft.paid_at
    invoice_draft.mark_paid(clock, idempotency_key)
    assert invoice_draft.paid_at == first_paid
    assert invoice_draft.status == InvoiceStatus.PAID

    # Попытка использования другого ключа (другая оплата)
    with pytest.raises(InvoiceOperationError):
        invoice_draft.mark_paid(clock, "123")
