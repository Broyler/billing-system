# src/billing_system/domain/errors/invoice_not_found.py
class InvoiceNotFoundError(Exception):
    """Ошибка об отсутствии нужного счета в бд."""
