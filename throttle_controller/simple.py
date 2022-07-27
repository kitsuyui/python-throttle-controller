import datetime
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Type

from .protocol import ThrottleController


@dataclass
class SimpleThrottleController:
    default_cooldown_time: datetime.timedelta = datetime.timedelta(seconds=3.0)
    last_use_times: Dict[str, datetime.datetime] = field(default_factory=dict)
    cooldown_times: Dict[str, datetime.timedelta] = field(default_factory=dict)

    def cooldown_time_for(self, key: str) -> datetime.timedelta:
        return self.cooldown_times.get(key, self.default_cooldown_time)

    def record_use_time(self, key: str, use_time: datetime.datetime) -> None:
        self.last_use_times[key] = use_time

    def record_use_time_as_now(self, key: str) -> None:
        self.record_use_time(key, datetime.datetime.now())

    def wait_if_needed(self, key: str) -> None:
        if not self._has_ever_used(key):
            return
        wait_time = self.wait_time_for(key)
        time.sleep(wait_time.total_seconds())

    def wait_time_for(self, key: str) -> datetime.timedelta:
        wait_time = self.next_available_time(key) - datetime.datetime.now()
        return max(wait_time, datetime.timedelta(seconds=0))

    def next_available_time(self, key: str) -> datetime.datetime:
        if not self._has_ever_used(key):
            return datetime.datetime.min

        interval = self.cooldown_time_for(key)
        return self.last_use_times[key] + interval

    def _has_ever_used(self, key: str) -> bool:
        return key in self.last_use_times


if TYPE_CHECKING:
    _: Type[ThrottleController] = SimpleThrottleController
