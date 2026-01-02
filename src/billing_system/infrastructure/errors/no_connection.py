# src/billing_system/infrastructure/errors/no_connection.py
class NoConnectionError(RuntimeError):
    """Ошибка для отсутствия подключения к базе данных."""
