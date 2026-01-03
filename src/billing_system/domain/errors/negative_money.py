# src/billing_system/domain/errors/negative_money.py
from .domain_error import DomainError


class NegativeMoneyError(DomainError):
    """Класс для ошибки при отрицательной сумме денег (инвариант)."""
