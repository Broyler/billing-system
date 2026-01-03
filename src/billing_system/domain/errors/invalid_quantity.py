# src/billing_system/domain/errors/invalid_quantity.py
from .domain_error import DomainError


class InvalidQuantityError(DomainError):
    """Класс ошибки для неправильного количества."""
