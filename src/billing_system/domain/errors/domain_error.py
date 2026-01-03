# src/billing_system/domain/errors/domain_error.py
class DomainError(Exception):
    """Базовый класс ошибки уровня домена для наследования."""

    status_code: int = 400
