import datetime
from unittest.mock import MagicMock, patch

from throttle_controller import SimpleThrottleController


def _make_fake_clock(
    start: datetime.datetime,
) -> tuple[MagicMock, list[datetime.datetime]]:
    current_time: list[datetime.datetime] = [start]

    def _fake_now() -> datetime.datetime:
        return current_time[0]

    fake_dt: MagicMock = MagicMock()
    fake_dt.datetime.now.side_effect = _fake_now
    fake_dt.datetime.min = datetime.datetime.min
    fake_dt.timedelta = datetime.timedelta
    return fake_dt, current_time


def _make_fake_sleep(
    current_time: list[datetime.datetime],
) -> MagicMock:
    def _fake_sleep(seconds: float) -> None:
        current_time[0] += datetime.timedelta(seconds=seconds)

    mock_sleep: MagicMock = MagicMock(side_effect=_fake_sleep)
    return mock_sleep


def test_throttling() -> None:
    cooldown_time = datetime.timedelta(seconds=1.0)
    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time)
    base = datetime.datetime(2020, 1, 1)

    fake_dt, current_time = _make_fake_clock(base)
    fake_sleep = _make_fake_sleep(current_time)

    with patch("throttle_controller.simple.datetime", fake_dt), patch(
        "throttle_controller.simple.time.sleep", fake_sleep,
    ):
        point1 = current_time[0]
        throttle.wait_if_needed("a")
        throttle.record_use_time_as_now("a")
        point2 = current_time[0]
        throttle.wait_if_needed("a")
        throttle.record_use_time_as_now("a")
        point3 = current_time[0]
        throttle.wait_if_needed("a")
        throttle.record_use_time_as_now("a")
        point4 = current_time[0]
        throttle.wait_if_needed("b")
        throttle.record_use_time_as_now("b")
        throttle.set_cooldown_time("b", 2.0)
        point5 = current_time[0]
        throttle.wait_if_needed("b")
        throttle.record_use_time_as_now("b")
        point6 = current_time[0]

    assert point2 == point1
    assert point3 - point2 == cooldown_time
    assert point4 - point3 == cooldown_time
    assert point5 == point4
    assert point6 - point5 == datetime.timedelta(seconds=2.0)


def test_with_statement() -> None:
    cooldown_time = datetime.timedelta(seconds=1.0)
    throttle = SimpleThrottleController.create(
        default_cooldown_time=cooldown_time,
    )
    base = datetime.datetime(2020, 1, 1)

    fake_dt, current_time = _make_fake_clock(base)
    fake_sleep = _make_fake_sleep(current_time)

    with patch("throttle_controller.simple.datetime", fake_dt), patch(
        "throttle_controller.simple.time.sleep", fake_sleep,
    ):
        point1 = current_time[0]
        with throttle.use("a"):
            pass
        point2 = current_time[0]
        with throttle.use("a"):
            pass
        point3 = current_time[0]

    assert point2 == point1
    assert point3 - point2 == cooldown_time


def test_set_cooldown_time() -> None:
    cooldown_time1 = datetime.timedelta(seconds=1.0)
    cooldown_time2 = datetime.timedelta(seconds=2.0)
    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time1)
    base = datetime.datetime(2020, 1, 1)

    fake_dt, current_time = _make_fake_clock(base)
    fake_sleep = _make_fake_sleep(current_time)

    with patch("throttle_controller.simple.datetime", fake_dt), patch(
        "throttle_controller.simple.time.sleep", fake_sleep,
    ):
        point1 = current_time[0]
        throttle.wait_if_needed("a")
        throttle.record_use_time_as_now("a")
        point2 = current_time[0]
        throttle.wait_if_needed("a")
        throttle.record_use_time_as_now("a")
        point3 = current_time[0]
        throttle.set_cooldown_time("a", 2.0)
        throttle.wait_if_needed("a")
        throttle.record_use_time_as_now("a")
        point4 = current_time[0]

    assert point2 == point1
    assert point3 - point2 == cooldown_time1
    assert point4 - point3 == cooldown_time2


def test_next_available_time() -> None:
    cooldown_time = datetime.timedelta(seconds=1.0)
    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time)
    assert throttle.next_available_time("a") == datetime.datetime.min
    base = datetime.datetime(2020, 1, 1)
    throttle.record_use_time("a", base)
    assert throttle.next_available_time("a") == base + cooldown_time


def test_evict() -> None:
    cooldown_time = datetime.timedelta(seconds=1.0)
    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time)
    throttle.record_use_time_as_now("a")
    throttle.set_cooldown_time("a", 2.0)
    assert throttle.next_available_time("a") != datetime.datetime.min

    throttle.evict("a")

    assert throttle.next_available_time("a") == datetime.datetime.min
    assert throttle.cooldown_time_for("a") == cooldown_time


def test_evict_unknown_key() -> None:
    cooldown_time = datetime.timedelta(seconds=1.0)
    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time)
    throttle.evict("nonexistent")


def test_clear() -> None:
    cooldown_time = datetime.timedelta(seconds=1.0)
    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time)
    throttle.record_use_time_as_now("a")
    throttle.record_use_time_as_now("b")
    throttle.set_cooldown_time("a", 2.0)

    throttle.clear()

    assert throttle.next_available_time("a") == datetime.datetime.min
    assert throttle.next_available_time("b") == datetime.datetime.min
    assert throttle.cooldown_time_for("a") == cooldown_time
