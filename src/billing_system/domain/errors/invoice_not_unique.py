# src/billing_system/domain/errors/invoice_not_unique.py
from .domain_error import DomainError


class InvoiceNotUniqueError(DomainError):
    """Ошибка повторения первичного ключа счета."""
