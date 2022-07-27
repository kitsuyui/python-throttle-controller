# throttle-controller

## Usage

```python
from throttle_controller import SimpleThrottleController

throttle = SimpleThrottleController(default_cooldown_time=3.0)
throttle.wait_if_needed("http://example.com/path/to/api")
throttle.record_use_time_as_now("http://example.com/path/to/api")
... # requests
throttle.wait_if_needed("http://example.com/path/to/api")  # wait 3.0 seconds
throttle.record_use_time_as_now("http://example.com/path/to/api")
```

# Caution

Currently this package supports only to use in single thread / single process use-cases.

# LICENSE

The 3-Clause BSD License. See also LICENSE file.
