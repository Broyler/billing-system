# src/billing_system/domain/errors/invalid_money.py
from .domain_error import DomainError


class InvalidMoneyError(DomainError):
    """Ошибка для некорректного значения денег, напр. бесконечность."""
