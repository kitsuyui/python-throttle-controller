import concurrent.futures
import datetime
from collections.abc import Callable

import pytest
from throttle_controller import SimpleThrottleController


Clock = tuple[Callable[[], datetime.datetime], Callable[[float], None]]


def thread_error(callback: Callable[[], None]) -> BaseException | None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(callback)
        return future.exception(timeout=1.0)


def manual_clock(start: datetime.datetime) -> Clock:
    current_time = start

    def now() -> datetime.datetime:
        return current_time

    def sleep(seconds: float) -> None:
        nonlocal current_time
        current_time += datetime.timedelta(seconds=seconds)

    return now, sleep


def test_throttling(monkeypatch: pytest.MonkeyPatch) -> None:
    cooldown_time = datetime.timedelta(seconds=1.0)
    now, sleep = manual_clock(datetime.datetime(2026, 1, 2, 3, 4, 5))
    monkeypatch.setattr("throttle_controller.simple.time.sleep", sleep)
    throttle = SimpleThrottleController(
        default_cooldown_time=cooldown_time,
        now=now,
    )

    point1 = now()
    throttle.wait_if_needed("a")
    throttle.record_use_time_as_now("a")
    point2 = now()
    throttle.wait_if_needed("a")
    throttle.record_use_time_as_now("a")
    point3 = now()
    throttle.wait_if_needed("a")
    throttle.record_use_time_as_now("a")
    point4 = now()
    throttle.wait_if_needed("b")
    throttle.record_use_time_as_now("b")
    throttle.set_cooldown_time("b", 2.0)
    point5 = now()
    throttle.wait_if_needed("b")
    throttle.record_use_time_as_now("b")
    point6 = now()

    assert point2 - point1 == datetime.timedelta()
    assert point3 - point2 == cooldown_time
    assert point4 - point3 == cooldown_time
    assert point5 - point4 == datetime.timedelta()
    assert point6 - point5 == datetime.timedelta(seconds=2.0)


def test_with_statement(monkeypatch: pytest.MonkeyPatch) -> None:
    cooldown_time = datetime.timedelta(seconds=1.0)
    now, sleep = manual_clock(datetime.datetime(2026, 1, 2, 3, 4, 5))
    monkeypatch.setattr("throttle_controller.simple.time.sleep", sleep)
    throttle = SimpleThrottleController.create(
        default_cooldown_time=cooldown_time,
        now=now,
    )

    point1 = now()
    with throttle.use("a"):
        pass
    point2 = now()
    with throttle.use("a"):
        pass
    point3 = now()

    assert point2 - point1 == datetime.timedelta()
    assert point3 - point2 == cooldown_time


def test_set_cooldown_time(monkeypatch: pytest.MonkeyPatch) -> None:
    cooldown_time1 = datetime.timedelta(seconds=1.0)
    cooldown_time2 = datetime.timedelta(seconds=2.0)
    now, sleep = manual_clock(datetime.datetime(2026, 1, 2, 3, 4, 5))
    monkeypatch.setattr("throttle_controller.simple.time.sleep", sleep)

    throttle = SimpleThrottleController(
        default_cooldown_time=cooldown_time1,
        now=now,
    )
    point1 = now()
    throttle.wait_if_needed("a")
    throttle.record_use_time_as_now("a")
    point2 = now()
    throttle.wait_if_needed("a")
    throttle.record_use_time_as_now("a")
    point3 = now()
    throttle.set_cooldown_time("a", 2.0)
    throttle.wait_if_needed("a")
    throttle.record_use_time_as_now("a")
    point4 = now()

    assert point2 - point1 == datetime.timedelta()
    assert point3 - point2 == cooldown_time1
    assert point4 - point3 == cooldown_time2


def test_next_available_time() -> None:
    cooldown_time = datetime.timedelta(seconds=1.0)
    current_time = datetime.datetime(2026, 1, 2, 3, 4, 5)
    throttle = SimpleThrottleController(
        default_cooldown_time=cooldown_time,
        now=lambda: current_time,
    )

    assert throttle.next_available_time("a") == datetime.datetime.min
    throttle.record_use_time_as_now("a")
    assert throttle.next_available_time("a") == current_time + cooldown_time


def test_injected_clock_records_current_time() -> None:
    cooldown_time = datetime.timedelta(seconds=1.0)
    current_time = datetime.datetime(2026, 1, 2, 3, 4, 5)
    throttle = SimpleThrottleController(
        default_cooldown_time=cooldown_time,
        now=lambda: current_time,
    )

    throttle.record_use_time_as_now("a")

    assert throttle.last_use_times["a"] == current_time
    assert throttle.next_available_time("a") == current_time + cooldown_time


def test_injected_clock_controls_wait_time() -> None:
    cooldown_time = datetime.timedelta(seconds=1.0)
    current_times = iter(
        [
            datetime.datetime(2026, 1, 2, 3, 4, 5),
            datetime.datetime(2026, 1, 2, 3, 4, 5, 250000),
        ],
    )
    throttle = SimpleThrottleController.create(
        default_cooldown_time=cooldown_time,
        now=lambda: next(current_times),
    )

    throttle.record_use_time_as_now("a")

    assert throttle.wait_time_for("a") == datetime.timedelta(
        microseconds=750000,
    )


def test_cross_thread_use_raises_runtime_error() -> None:
    throttle = SimpleThrottleController.create(default_cooldown_time=1.0)
    error = thread_error(lambda: throttle.wait_if_needed("a"))

    assert isinstance(error, RuntimeError)
    assert "single-thread use" in str(error)


def test_cross_thread_record_as_now_does_not_call_clock() -> None:
    clock_calls = 0

    def now() -> datetime.datetime:
        nonlocal clock_calls
        clock_calls += 1
        return datetime.datetime(2026, 1, 2, 3, 4, 5)

    throttle = SimpleThrottleController.create(
        default_cooldown_time=1.0,
        now=now,
    )

    error = thread_error(lambda: throttle.record_use_time_as_now("a"))

    assert isinstance(error, RuntimeError)
    assert clock_calls == 0
    assert "a" not in throttle.last_use_times


def test_use_records_time_even_on_exception() -> None:
    """A body that raises still consumes the cooldown slot.

    ``use()`` records the use time *before* yielding control, so the
    throttle state is updated regardless of whether the body succeeds.
    """
    cooldown_time = datetime.timedelta(seconds=1.0)
    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time)

    assert throttle.next_available_time("a") == datetime.datetime.min

    try:
        with throttle.use("a"):
            raise RuntimeError("simulated failure")
    except RuntimeError:
        pass

    # The slot is consumed: next_available_time is in the future.
    assert throttle.next_available_time("a") > datetime.datetime.min


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


def test_to_dict_from_dict_round_trip() -> None:
    cooldown_time = datetime.timedelta(seconds=5.0)
    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time)
    use_time = datetime.datetime(2026, 1, 1, 12, 0, 0)
    throttle.record_use_time("api", use_time)
    throttle.set_cooldown_time("api", 10.0)

    data = throttle.to_dict()
    restored = SimpleThrottleController.from_dict(data)

    assert restored.default_cooldown_time == cooldown_time
    assert restored.last_use_times == {"api": use_time}
    assert restored.cooldown_times == {"api": datetime.timedelta(seconds=10.0)}
    assert restored.next_available_time("api") == throttle.next_available_time(
        "api",
    )


def test_to_dict_empty_state() -> None:
    cooldown_time = datetime.timedelta(seconds=3.0)
    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time)
    data = throttle.to_dict()

    assert data["default_cooldown_time"] == 3.0
    assert data["last_use_times"] == {}
    assert data["cooldown_times"] == {}

    restored = SimpleThrottleController.from_dict(data)
    assert restored.default_cooldown_time == cooldown_time
    assert restored.last_use_times == {}
    assert restored.cooldown_times == {}


def test_to_dict_json_compatible() -> None:
    import json

    cooldown_time = datetime.timedelta(seconds=2.0)
    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time)
    throttle.record_use_time("key1", datetime.datetime(2026, 6, 1, 0, 0, 0))

    data = throttle.to_dict()
    serialized = json.dumps(data)
    deserialized = json.loads(serialized)
    restored = SimpleThrottleController.from_dict(deserialized)

    assert restored.default_cooldown_time == cooldown_time
    assert restored.last_use_times == {
        "key1": datetime.datetime(2026, 6, 1, 0, 0, 0),
    }
