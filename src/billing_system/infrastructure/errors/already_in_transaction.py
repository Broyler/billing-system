# src/billing_system/infrastructure/errors/already_in_transaction.py
class AlreadyInTransactionError(Exception):
    """Ошибка запуска транзакций UOW повторно."""
