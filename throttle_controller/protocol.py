import contextlib
import datetime
from collections.abc import Generator, Hashable
from typing import Protocol  # pragma: no cover

Key = Hashable


class ThrottleController(Protocol):  # pragma: no cover
    """Structural protocol for throttle controllers.

    Implementations enforce a per-key cooldown: after each use the key is
    blocked until ``cooldown_time_for(key)`` has elapsed.
    """

    def cooldown_time_for(self, key: Key) -> datetime.timedelta:
        """Return the cooldown duration configured for *key*."""
        ...

    def record_use_time(
        self,
        key: Key,
        use_time: datetime.datetime,
    ) -> None:
        """Record that *key* was used at *use_time*."""
        ...

    def record_use_time_as_now(self, key: Key) -> None:
        """Record that *key* was used at the current wall-clock time."""
        ...

    def wait_if_needed(self, key: Key) -> None:
        """Block until *key* is no longer in cooldown."""
        ...

    def wait_time_for(self, key: Key) -> datetime.timedelta:
        """Return the remaining cooldown duration for *key* (≥ 0)."""
        ...

    def next_available_time(self, key: Key) -> datetime.datetime:
        """Return the earliest datetime at which *key* may be used again."""
        ...

    @contextlib.contextmanager
    def use(self, key: Key) -> Generator[None, None, None]:
        """Context manager: wait for *key*'s cooldown, then record the use."""
        self.wait_if_needed(key)
        self.record_use_time_as_now(key)
        yield
