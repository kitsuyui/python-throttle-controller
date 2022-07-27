import datetime

from throttle_controller.utils.interval import interval_to_timedelta


def test_interval_to_timedelta() -> None:
    assert interval_to_timedelta(None) == datetime.timedelta(0)
    assert interval_to_timedelta(1) == datetime.timedelta(seconds=1)
    assert interval_to_timedelta(1.0) == datetime.timedelta(seconds=1)
    assert interval_to_timedelta(datetime.timedelta(seconds=1)) == datetime.timedelta(
        seconds=1
    )
