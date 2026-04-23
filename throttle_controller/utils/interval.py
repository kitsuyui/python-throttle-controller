from __future__ import annotations

import datetime

Interval = datetime.timedelta | float | int


def interval_to_timedelta(interval: Interval | None) -> datetime.timedelta:
    if isinstance(interval, datetime.timedelta):
        return interval
    seconds = 0 if interval is None else interval
    return datetime.timedelta(seconds=seconds)
