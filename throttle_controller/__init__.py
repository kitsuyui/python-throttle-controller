"""Throttle controller: rate-limiting primitives for Python applications.

Usage::

    from throttle_controller import SimpleThrottleController

    controller = SimpleThrottleController.create(default_cooldown_time=1.0)
    with controller.use("my-key"):
        ...  # at most once per second per key
"""

from importlib.metadata import version

from .protocol import ThrottleController
from .simple import SimpleThrottleController

__version__ = version("throttle-controller")
__all__ = ["SimpleThrottleController", "ThrottleController", "__version__"]
