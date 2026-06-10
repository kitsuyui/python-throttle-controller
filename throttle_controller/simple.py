from __future__ import annotations

import datetime
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from .protocol import Key, ThrottleController
from .utils.interval import Interval, interval_to_timedelta


@dataclass
class SimpleThrottleController(ThrottleController):
    """In-memory throttle controller with per-key cooldown tracking.

    Tracks the last-use time for each key and enforces a minimum interval
    (cooldown) between consecutive uses.  The default cooldown applies when
    no per-key override has been set via :meth:`set_cooldown_time`.

    Create via the factory method::

        ctrl = SimpleThrottleController.create(default_cooldown_time=1.0)
    """

    default_cooldown_time: datetime.timedelta
    last_use_times: dict[Key, datetime.datetime] = field(default_factory=dict)
    cooldown_times: dict[Key, datetime.timedelta] = field(default_factory=dict)
    max_wait: datetime.timedelta | None = None
    now: Callable[[], datetime.datetime] = field(
        default=datetime.datetime.now,
        repr=False,
    )
    _owner_thread_id: int = field(
        default_factory=threading.get_ident,
        init=False,
        repr=False,
    )

    @classmethod
    def create(
        cls,
        *,
        default_cooldown_time: Interval,
        max_wait: Interval | None = None,
        now: Callable[[], datetime.datetime] = datetime.datetime.now,
    ) -> SimpleThrottleController:
        """Create a controller with the given default cooldown.

        Args:
            default_cooldown_time: Cooldown as a :class:`~datetime.timedelta`,
                float seconds, or int seconds.
        """
        return cls(
            default_cooldown_time=interval_to_timedelta(default_cooldown_time),
            max_wait=interval_to_timedelta(max_wait)
            if max_wait is not None
            else None,
            now=now,
        )

    def cooldown_time_for(self, key: Key) -> datetime.timedelta:
        """Return the effective cooldown duration for *key*.

        Returns the per-key override if one has been set via
        :meth:`set_cooldown_time`, otherwise the default cooldown.
        """
        self._ensure_owner_thread()
        return self.cooldown_times.get(key, self.default_cooldown_time)

    def record_use_time(self, key: Key, use_time: datetime.datetime) -> None:
        """Record that *key* was used at *use_time*."""
        self._ensure_owner_thread()
        if use_time.tzinfo is not None:
            raise ValueError(
                f"record_use_time requires a timezone-naive datetime, "
                f"got timezone-aware datetime with tzinfo={use_time.tzinfo!r}",
            )
        self.last_use_times[key] = use_time

    def record_use_time_as_now(self, key: Key) -> None:
        """Record that *key* was used at the current time.

        The current time is obtained from the injected ``now`` callable
        (the wall clock by default).
        """
        self._ensure_owner_thread()
        self.record_use_time(key, self.now())

    def wait_if_needed(self, key: Key) -> None:
        """Sleep until *key*'s cooldown has elapsed.

        No-op when *key* has never been used.
        """
        self._ensure_owner_thread()
        if not self._has_ever_used(key):
            return
        wait_time = self.wait_time_for(key)
        self._enforce_max_wait(wait_time)
        time.sleep(wait_time.total_seconds())

    def _enforce_max_wait(self, wait_time: datetime.timedelta) -> None:
        if self.max_wait is not None and wait_time > self.max_wait:
            raise TimeoutError(
                f"wait time {wait_time} exceeds max_wait {self.max_wait}",
            )

    def wait_time_for(self, key: Key) -> datetime.timedelta:
        """Return the remaining cooldown for *key*, or zero if ready."""
        self._ensure_owner_thread()
        wait_time = self.next_available_time(key) - self.now()
        return max(wait_time, datetime.timedelta(seconds=0))

    def next_available_time(self, key: Key) -> datetime.datetime:
        """Return the earliest time at which *key* may be used again.

        Returns :attr:`~datetime.datetime.min` when *key* has never been used.
        """
        self._ensure_owner_thread()
        if not self._has_ever_used(key):
            return datetime.datetime.min

        interval = self.cooldown_time_for(key)
        return self.last_use_times[key] + interval

    def _has_ever_used(self, key: Key) -> bool:
        return key in self.last_use_times

    def set_cooldown_time(self, key: Key, cooldown_time: Interval) -> None:
        """Set a per-key cooldown override.

        Args:
            key: The throttle key to configure.
            cooldown_time: New cooldown as a :class:`~datetime.timedelta`,
                float seconds, or int seconds.
        """
        self._ensure_owner_thread()
        self.cooldown_times[key] = interval_to_timedelta(cooldown_time)

    def evict(self, key: Key) -> None:
        self._ensure_owner_thread()
        self.last_use_times.pop(key, None)
        self.cooldown_times.pop(key, None)

    def clear(self) -> None:
        self._ensure_owner_thread()
        self.last_use_times.clear()
        self.cooldown_times.clear()

    def _ensure_owner_thread(self) -> None:
        current_thread_id = threading.get_ident()
        self._raise_if_wrong_thread(current_thread_id, self._owner_thread_id)

    @staticmethod
    def _raise_if_wrong_thread(
        current_thread_id: int,
        owner_thread_id: int,
    ) -> None:
        if owner_thread_id != current_thread_id:
            message = (
                "SimpleThrottleController instances support only "
                "single-thread use"
            )
            raise RuntimeError(message)
