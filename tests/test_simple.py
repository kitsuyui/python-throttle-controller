import datetime

from throttle_controller import SimpleThrottleController


def test_throttling() -> None:
    alpha = datetime.timedelta(seconds=0.01)
    cooldown_time = datetime.timedelta(seconds=1.0)
    throttle_controller = SimpleThrottleController(default_cooldown_time=cooldown_time)

    point1 = datetime.datetime.now()
    throttle_controller.wait_if_needed("a")
    throttle_controller.record_use_time_as_now("a")
    point2 = datetime.datetime.now()
    throttle_controller.wait_if_needed("a")
    throttle_controller.record_use_time_as_now("a")
    point3 = datetime.datetime.now()
    throttle_controller.wait_if_needed("a")
    throttle_controller.record_use_time_as_now("a")
    point4 = datetime.datetime.now()
    throttle_controller.wait_if_needed("b")
    throttle_controller.record_use_time_as_now("b")
    point5 = datetime.datetime.now()

    assert point2 - point1 <= alpha
    assert cooldown_time - alpha <= point3 - point2 <= cooldown_time + alpha
    assert cooldown_time - alpha <= point4 - point3 <= cooldown_time + alpha
    assert point5 - point4 <= alpha
