# src/billing_system/domain/errors/invoice_not_found.py
from .domain_error import DomainError


class InvoiceNotFoundError(DomainError):
    """Ошибка об отсутствии нужного счета в бд."""

    status_code = 404
