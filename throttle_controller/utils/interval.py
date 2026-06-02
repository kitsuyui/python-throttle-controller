from __future__ import annotations

import datetime

IntervalSeconds = float | int
Interval = datetime.timedelta | IntervalSeconds


def _seconds_to_timedelta(seconds: float | int) -> datetime.timedelta:
    try:
        return datetime.timedelta(seconds=seconds)
    except (OverflowError, ValueError) as exc:
        raise ValueError(
            f"interval must be a finite number, got {seconds!r}",
        ) from exc


def interval_to_timedelta(interval: Interval | None) -> datetime.timedelta:
    if isinstance(interval, datetime.timedelta):
        return interval
    seconds = 0 if interval is None else interval
    return _seconds_to_timedelta(seconds)
