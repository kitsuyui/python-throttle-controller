from __future__ import annotations

import datetime
import time
from dataclasses import dataclass, field

from .protocol import Key, ThrottleController
from .utils.interval import Interval, interval_to_timedelta


@dataclass
class SimpleThrottleController(ThrottleController):
    default_cooldown_time: datetime.timedelta
    last_use_times: dict[Key, datetime.datetime] = field(default_factory=dict)
    cooldown_times: dict[Key, datetime.timedelta] = field(default_factory=dict)
    _last_monotonic_times: dict[Key, float] = field(
        default_factory=dict, init=False, repr=False, compare=False,
    )

    @classmethod
    def create(
        cls,
        *,
        default_cooldown_time: Interval,
    ) -> SimpleThrottleController:
        return cls(
            default_cooldown_time=interval_to_timedelta(default_cooldown_time),
        )

    def cooldown_time_for(self, key: Key) -> datetime.timedelta:
        return self.cooldown_times.get(key, self.default_cooldown_time)

    def record_use_time(self, key: Key, use_time: datetime.datetime) -> None:
        self.last_use_times[key] = use_time

    def record_use_time_as_now(self, key: Key) -> None:
        self.record_use_time(key, datetime.datetime.now())
        self._last_monotonic_times[key] = time.monotonic()

    def wait_if_needed(self, key: Key) -> None:
        if not self._has_ever_used(key):
            return
        wait_time = self.wait_time_for(key)
        time.sleep(wait_time.total_seconds())

    def wait_time_for(self, key: Key) -> datetime.timedelta:
        if key in self._last_monotonic_times:
            return datetime.timedelta(
                seconds=self._monotonic_seconds_remaining(key),
            )
        wait_time = self.next_available_time(key) - datetime.datetime.now()
        return max(wait_time, datetime.timedelta(seconds=0))

    def _monotonic_seconds_remaining(self, key: Key) -> float:
        elapsed = time.monotonic() - self._last_monotonic_times[key]
        return max(self.cooldown_time_for(key).total_seconds() - elapsed, 0.0)

    def next_available_time(self, key: Key) -> datetime.datetime:
        if not self._has_ever_used(key):
            return datetime.datetime.min

        interval = self.cooldown_time_for(key)
        return self.last_use_times[key] + interval

    def _has_ever_used(self, key: Key) -> bool:
        return key in self.last_use_times

    def set_cooldown_time(self, key: Key, cooldown_time: Interval) -> None:
        self.cooldown_times[key] = interval_to_timedelta(cooldown_time)

    def evict(self, key: Key) -> None:
        self.last_use_times.pop(key, None)
        self.cooldown_times.pop(key, None)

    def clear(self) -> None:
        self.last_use_times.clear()
        self.cooldown_times.clear()
