from __future__ import annotations

import datetime
import time
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

    @classmethod
    def create(
        cls, *, default_cooldown_time: Interval,
    ) -> SimpleThrottleController:
        """Create a controller with the given default cooldown.

        Args:
            default_cooldown_time: Cooldown as a :class:`~datetime.timedelta`,
                float seconds, or int seconds.
        """
        return cls(
            default_cooldown_time=interval_to_timedelta(default_cooldown_time),
        )

    def cooldown_time_for(self, key: Key) -> datetime.timedelta:
        """Return the effective cooldown duration for *key*.

        Returns the per-key override if one has been set via
        :meth:`set_cooldown_time`, otherwise the default cooldown.
        """
        return self.cooldown_times.get(key, self.default_cooldown_time)

    def record_use_time(self, key: Key, use_time: datetime.datetime) -> None:
        """Record that *key* was used at *use_time*."""
        self.last_use_times[key] = use_time

    def record_use_time_as_now(self, key: Key) -> None:
        """Record that *key* was used at the current wall-clock time."""
        self.record_use_time(key, datetime.datetime.now())

    def wait_if_needed(self, key: Key) -> None:
        """Sleep until *key*'s cooldown has elapsed.

        No-op when *key* has never been used.
        """
        if not self._has_ever_used(key):
            return
        wait_time = self.wait_time_for(key)
        time.sleep(wait_time.total_seconds())

    def wait_time_for(self, key: Key) -> datetime.timedelta:
        """Return the remaining cooldown for *key*, or zero if ready."""
        wait_time = self.next_available_time(key) - datetime.datetime.now()
        return max(wait_time, datetime.timedelta(seconds=0))

    def next_available_time(self, key: Key) -> datetime.datetime:
        """Return the earliest time at which *key* may be used again.

        Returns :attr:`~datetime.datetime.min` when *key* has never been used.
        """
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
        self.cooldown_times[key] = interval_to_timedelta(cooldown_time)
