import datetime

import pytest

from throttle_controller.utils.interval import interval_to_timedelta


def test_interval_to_timedelta() -> None:
    assert interval_to_timedelta(None) == datetime.timedelta(0)
    assert interval_to_timedelta(1) == datetime.timedelta(seconds=1)
    assert interval_to_timedelta(1.0) == datetime.timedelta(seconds=1)
    assert interval_to_timedelta(
        datetime.timedelta(seconds=1),
    ) == datetime.timedelta(seconds=1)


@pytest.mark.parametrize(
    "interval",
    [
        -1,
        -1.0,
        datetime.timedelta(seconds=-1),
    ],
)
def test_interval_to_timedelta_rejects_negative_values(
    interval: datetime.timedelta | float | int,
) -> None:
    with pytest.raises(
        ValueError,
        match="cooldown interval must be non-negative",
    ):
        interval_to_timedelta(interval)
