# src/billing_system/domain/errors/invoice_currency_mismatch.py
class InvoiceCurrencyMismatchError(Exception):
    """Ошибка несовпадения валюты в счете."""
