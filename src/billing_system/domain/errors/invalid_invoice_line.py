# src/billing_system/domain/errors/invalid_invoice_line.py
from .domain_error import DomainError


class InvalidInvoiceLineError(DomainError):
    """Ошибка для некорректных строк в счете."""
