# src/billing_system/domain/errors/invalid_invoice_line.py
class InvalidInvoiceLineError(Exception):
    """Ошибка для некорректных строк в счете."""
