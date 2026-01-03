# src/billing_system/domain/errors/invoice_operation.py
from .domain_error import DomainError


class InvoiceOperationError(DomainError):
    """Ошибка пользователя при взаимодействии со счетом."""
