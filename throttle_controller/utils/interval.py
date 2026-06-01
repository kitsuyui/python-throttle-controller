from __future__ import annotations

import datetime

Interval = datetime.timedelta | float | int


def interval_to_timedelta(interval: Interval | None) -> datetime.timedelta:
    if interval is None:
        return datetime.timedelta(0)
    return _ensure_non_negative(_interval_to_timedelta(interval))


def _interval_to_timedelta(interval: Interval) -> datetime.timedelta:
    if isinstance(interval, datetime.timedelta):
        return interval
    return datetime.timedelta(seconds=interval)


def _ensure_non_negative(
    cooldown_time: datetime.timedelta,
) -> datetime.timedelta:
    if cooldown_time < datetime.timedelta(0):
        msg = "cooldown interval must be non-negative"
        raise ValueError(msg)
    return cooldown_time
