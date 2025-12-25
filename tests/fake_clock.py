# tests/fake_clock.py
import datetime

from billing_system.domain.protocols import ClockProtocol


class FakeClock(ClockProtocol):
    """Инфра класс для протокола фейк часов для тестов."""

    def __init__(self) -> None:
        self.__sequence = list(range(1, 11))

    def now(self) -> datetime.datetime:
        """Возвращает последующие дни по кругу."""
        day = self.__sequence.pop(0)
        self.__sequence.append(day)
        return datetime.datetime(
            year=2020,
            month=11,
            day=day,
            tzinfo=datetime.UTC,
        )
