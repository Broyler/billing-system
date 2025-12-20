# src/billing_system/domain/errors/invalid_money.py
class InvalidMoneyError(Exception):
    """Ошибка для некорректного значения денег, напр. бесконечность."""
