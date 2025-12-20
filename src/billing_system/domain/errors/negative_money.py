# src/billing_system/domain/errors/negative_money.py
class NegativeMoneyError(Exception):
    """Класс для ошибки при отрицательной сумме денег (инвариант)."""
