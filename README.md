# throttle-controller

[![Python](https://img.shields.io/pypi/pyversions/throttle-controller.svg?style=plastic)](https://badge.fury.io/py/throttle-controller)
[![PyPI version shields.io](https://img.shields.io/pypi/v/throttle-controller.svg)](https://pypi.python.org/pypi/throttle-controller/)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
![Coverage](https://raw.githubusercontent.com/kitsuyui/octocov-central/main/badges/kitsuyui/python-throttle-controller/coverage.svg)

## Motivation

This package provides a simple throttle controller for general use-cases.
For example, you can use this package to throttle API requests to avoid rate-limiting.

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

### Deterministic clock for tests

Pass `now` when you need deterministic tests or replayable behavior:

```python
import datetime
from throttle_controller import SimpleThrottleController

fixed_time = datetime.datetime(2026, 1, 2, 3, 4, 5)
throttle = SimpleThrottleController.create(
    default_cooldown_time=3.0,
    now=lambda: fixed_time,
)
```

## Stability

This package is currently in **Alpha** (`Development Status :: 3 - Alpha`).

- Breaking changes may occur between minor versions while in Alpha.
- The package will be considered for Beta promotion when thread-safe and multi-process support is implemented.
- A stable (1.0) release is planned after Beta validation.

## Cooldown timing behaviour

The `use()` context manager and the manual `record_use_time_as_now()` call record
the **start** of each use, not the end. This means the cooldown is measured
**start-to-start**: the next call may proceed once `cooldown_time` has elapsed
since the *start* of the previous call.

```
call 1 start ──────────── call 1 body (2.9 s) ────── call 1 end
             │
             └── cooldown_time = 3.0 s ──────────────────────────► call 2 may start
                                                               (only 0.1 s after call 1 ends)
```

If you need **end-to-start** behaviour (next call waits until at least
`cooldown_time` after the *previous call finishes*), record the time after your
work completes instead of relying on the context manager:

```python
throttle.wait_if_needed(key)
result = do_work()          # your code here
throttle.record_use_time_as_now(key)   # record end of work
```

# Caution

Currently this package supports only to use in single thread / single process use-cases.
Reusing the same controller instance from multiple threads raises `RuntimeError`.

## Development

This repository uses [lefthook](https://lefthook.dev/) to run the same checks as CI
locally, so problems surface before they reach CI.

```sh
# Install dependencies
uv sync

# Install the Git hooks (once; requires lefthook on your PATH)
lefthook install
```

Once installed, the hooks run automatically:

- **pre-commit**: `uv run poe check`
- **pre-push**: `uv run poe check` and `uv run poe test`

You can also run the checks manually:

```sh
uv run poe check
uv run poe test
```

CI still runs the full matrix (see `.github/workflows/`); the hooks only bring that
feedback earlier on your machine.

# LICENSE

The 3-Clause BSD License. See also LICENSE file.
