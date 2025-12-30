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
