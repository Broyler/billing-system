# tests/unit/test_system_clock.py
import datetime

from billing_system.infrastructure.protocols import SystemClock


def test_now_matches() -> None:
    clock = SystemClock()
    res = clock.now()
    now = datetime.datetime.now(tz=datetime.UTC)
    delta = abs(now - res).total_seconds()
    assert delta < 1 / 10
