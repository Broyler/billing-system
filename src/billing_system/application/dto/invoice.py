# src/billing_system/application/dto/invoice.py
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CreateInvoiceRequest(BaseModel):
    """DTO для данных, необходимых для создания счета."""

    id: UUID
    currency: str


class InvoiceAddLineRequest(BaseModel):
    """DTO для данных, необходимых для добавления строчки в счет.

    Принимает id счета, количество, стоимость и описание.
    """

    invoice_id: UUID
    amount: Decimal
    quantity: Decimal
    description: str


class IssueInvoiceRequest(BaseModel):
    """DTO для данных, необходимых для выставления счета."""

    invoice_id: UUID


class VoidInvoiceRequest(BaseModel):
    """DTO для данных аннулирования счета."""

    invoice_id: UUID
    idempotency_key: str


class LineRead(BaseModel):
    """DTO для данных возвращаемых при чтении строчки."""

    amount: Decimal
    quantity: Decimal
    description: str


class InvoiceRead(BaseModel):
    """DTO для данных выдаваемых на чтение со счета."""

    invoice_id: UUID
    currency: str
    status: str
    lines: list[LineRead]
    discount: Decimal | None
    tax: Decimal | None
    subtotal: Decimal
    total: Decimal


class GetInvoiceRequest(BaseModel):
    """DTO для данных получения одного счета."""

    invoice_id: UUID
