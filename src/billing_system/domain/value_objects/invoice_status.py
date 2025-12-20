# src/billing_system/domain/value_objects/invoice_status.py
# InvoiceStatus Value Object для системы, статус счета (Enum)
from enum import Enum


class InvoiceStatus(Enum):
    """Класс для Value Object статуса счета."""

    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAID = "PAID"
    VOID = "VOID"
