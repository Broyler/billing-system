# src/billing_system/domain/errors/currency_mismatch.py
class CurrencyMismatchError(Exception):
    """Класс ошибки при несовпадении валют."""
