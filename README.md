# throttle-controller

[![Python](https://img.shields.io/pypi/pyversions/throttle-controller.svg?style=plastic)](https://badge.fury.io/py/throttle-controller)
[![PyPI version shields.io](https://img.shields.io/pypi/v/throttle-controller.svg)](https://pypi.python.org/pypi/throttle-controller/)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![codecov](https://codecov.io/gh/kitsuyui/python-throttle-controller/branch/main/graph/badge.svg?token=90X7WXZDD2)](https://codecov.io/gh/kitsuyui/python-throttle-controller)

## Usage

```python
from throttle_controller import SimpleThrottleController

throttle = SimpleThrottleController.create(default_cooldown_time=3.0)
throttle.wait_if_needed("http://example.com/path/to/api")
throttle.record_use_time_as_now("http://example.com/path/to/api")
... # requests
throttle.wait_if_needed("http://example.com/path/to/api")  # wait 3.0 seconds
throttle.record_use_time_as_now("http://example.com/path/to/api")
```

### `with` statement

```python
from throttle_controller import SimpleThrottleController
throttle = SimpleThrottleController.create(default_cooldown_time=3.0)

for _ in range(10):
    with throttle.use("http://example.com/path/to/api"):
        # wait if cooldown needed
        requests.get("http://example.com/path/to/api")
```

# Caution

Currently this package supports only to use in single thread / single process use-cases.

# LICENSE

The 3-Clause BSD License. See also LICENSE file.
