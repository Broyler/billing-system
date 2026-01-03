# src/billing_system/domain/errors/invoice_currency_mismatch.py
from .domain_error import DomainError


class InvoiceCurrencyMismatchError(DomainError):
    """Ошибка несовпадения валюты в счете."""
