# src/billing_system/domain/errors/currency_mismatch.py
from .domain_error import DomainError


class CurrencyMismatchError(DomainError):
    """Класс ошибки при несовпадении валют."""
