# src/billing_system/domain/protocols/clock.py
from datetime import datetime
from typing import Protocol


class ClockProtocol(Protocol):
    """Абстрактный протокол часов для инъекции."""

    def now(self) -> datetime:
        """Метод должен возвращать текущее время."""
        ...
