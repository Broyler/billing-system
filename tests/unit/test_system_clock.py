# tests/unit/test_system_clock.py
import datetime

from billing_system.infrastructure.protocols import SystemClock


def test_now() -> None:
    clock = SystemClock()
    res = clock.now()
    now = datetime.datetime.now(tz=datetime.UTC)
    delta = abs(now - res)
    assert delta.total_seconds() < 1
