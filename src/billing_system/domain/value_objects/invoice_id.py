# src/billing_system/domain/value_objects/invoice_id.py
# InvoiceId Value Object для системы, Id счета (обертчик UUID)
from typing import NewType
from uuid import UUID

InvoiceId = NewType("InvoiceId", UUID)
