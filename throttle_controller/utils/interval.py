from __future__ import annotations

import datetime
from typing import Optional, Union

Interval = Union[datetime.timedelta, float, int]


def interval_to_timedelta(interval: Optional[Interval]) -> datetime.timedelta:
    if interval is None:
        return datetime.timedelta(seconds=0)
    if isinstance(interval, datetime.timedelta):
        return interval
    return datetime.timedelta(seconds=interval)
