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
    throttle = SimpleThrottleController.create(default_cooldown_time=cooldown_time)

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
