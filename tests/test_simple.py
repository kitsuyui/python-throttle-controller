import datetime

from throttle_controller import SimpleThrottleController


def test_throttling() -> None:
    alpha = datetime.timedelta(seconds=0.01)
    cooldown_time = datetime.timedelta(seconds=1.0)
    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time)

    point1 = datetime.datetime.now()
    throttle.wait_if_needed("a")
    throttle.record_use_time_as_now("a")
    point2 = datetime.datetime.now()
    throttle.wait_if_needed("a")
    throttle.record_use_time_as_now("a")
    point3 = datetime.datetime.now()
    throttle.wait_if_needed("a")
    throttle.record_use_time_as_now("a")
    point4 = datetime.datetime.now()
    throttle.wait_if_needed("b")
    throttle.record_use_time_as_now("b")
    throttle.set_cooldown_time("b", 2.0)
    point5 = datetime.datetime.now()
    throttle.wait_if_needed("b")
    throttle.record_use_time_as_now("b")
    point6 = datetime.datetime.now()

    assert point2 - point1 <= alpha
    assert cooldown_time - alpha <= point3 - point2 <= cooldown_time + alpha
    assert cooldown_time - alpha <= point4 - point3 <= cooldown_time + alpha
    assert point5 - point4 <= alpha
    assert point6 - point5 <= datetime.timedelta(seconds=2.0) + alpha


def test_with_statement() -> None:
    alpha = datetime.timedelta(seconds=0.01)
    cooldown_time = datetime.timedelta(seconds=1.0)
    throttle = SimpleThrottleController.create(
        default_cooldown_time=cooldown_time,
    )

    point1 = datetime.datetime.now()
    with throttle.use("a"):
        pass
    point2 = datetime.datetime.now()
    with throttle.use("a"):
        pass
    point3 = datetime.datetime.now()

    assert point2 - point1 <= alpha
    assert cooldown_time - alpha < point3 - point2 <= cooldown_time + alpha


def test_set_cooldown_time() -> None:
    alpha = datetime.timedelta(seconds=0.01)
    cooldown_time1 = datetime.timedelta(seconds=1.0)
    cooldown_time2 = datetime.timedelta(seconds=2.0)

    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time1)
    point1 = datetime.datetime.now()
    throttle.wait_if_needed("a")
    throttle.record_use_time_as_now("a")
    point2 = datetime.datetime.now()
    throttle.wait_if_needed("a")
    throttle.record_use_time_as_now("a")
    point3 = datetime.datetime.now()
    throttle.set_cooldown_time("a", 2.0)
    throttle.wait_if_needed("a")
    throttle.record_use_time_as_now("a")
    point4 = datetime.datetime.now()

    assert point2 - point1 <= alpha
    assert cooldown_time1 - alpha <= point3 - point2 <= cooldown_time1 + alpha
    assert cooldown_time2 - alpha <= point4 - point3 <= cooldown_time2 + alpha


def test_next_available_time() -> None:
    cooldown_time = datetime.timedelta(seconds=1.0)
    throttle = SimpleThrottleController(default_cooldown_time=cooldown_time)
    assert throttle.next_available_time("a") == datetime.datetime.min
    point = datetime.datetime.now()
    throttle.record_use_time_as_now("a")
    assert throttle.next_available_time("a") > point


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
