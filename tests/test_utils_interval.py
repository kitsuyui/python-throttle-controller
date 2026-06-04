import datetime

from throttle_controller.utils.interval import IntervalSeconds, interval_to_timedelta


def test_interval_to_timedelta() -> None:
    assert interval_to_timedelta(None) == datetime.timedelta(0)
    assert interval_to_timedelta(1) == datetime.timedelta(seconds=1)
    assert interval_to_timedelta(1.0) == datetime.timedelta(seconds=1)
    assert interval_to_timedelta(
        datetime.timedelta(seconds=1),
    ) == datetime.timedelta(seconds=1)


def test_interval_seconds_type_is_float_or_int() -> None:
    seconds: IntervalSeconds = 2.5
    assert interval_to_timedelta(seconds) == datetime.timedelta(seconds=2.5)
    whole: IntervalSeconds = 3
    assert interval_to_timedelta(whole) == datetime.timedelta(seconds=3)
