from importlib.metadata import version

from .protocol import ThrottleController
from .simple import SimpleThrottleController

__version__ = version("throttle-controller")
__all__ = ["SimpleThrottleController", "ThrottleController", "__version__"]
