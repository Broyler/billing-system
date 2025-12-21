# src/billing_system/infrastructure/protocols/system_clock.py
import datetime

from billing_system.domain.protocols import Clock


class SystemClock(Clock):
    """Инфра класс для протокола часов, исп. системное время."""

    def now(self) -> datetime.datetime:
        """Текущее время через системные часы, UTC час. пояс."""
        return datetime.datetime.now(tz=datetime.UTC)
