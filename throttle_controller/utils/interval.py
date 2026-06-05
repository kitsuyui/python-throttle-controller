"""Utilities for converting interval values to :class:`~datetime.timedelta`."""

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
    """Convert an interval value to a :class:`~datetime.timedelta`.

    Accepts a :class:`~datetime.timedelta` (returned as-is), a numeric number
    of seconds (``int`` or ``float``), or ``None`` (treated as 0 seconds).
    Raises :exc:`ValueError` for non-finite values such as ``inf`` or ``nan``.

    Examples::

        >>> import datetime
        >>> interval_to_timedelta(1.5)
        datetime.timedelta(seconds=1, microseconds=500000)
        >>> interval_to_timedelta(datetime.timedelta(seconds=2))
        datetime.timedelta(seconds=2)
        >>> interval_to_timedelta(None)
        datetime.timedelta(0)
    """
    if isinstance(interval, datetime.timedelta):
        return interval
    seconds = 0 if interval is None else interval
    return _seconds_to_timedelta(seconds)
