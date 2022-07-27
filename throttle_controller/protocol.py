import datetime
from typing import Protocol


class ThrottleController(Protocol):  # pragma: no cover
    def cooldown_time_for(self, key: str) -> datetime.timedelta:
        ...

    def record_use_time(self, key: str, use_time: datetime.datetime) -> None:
        ...

    def record_use_time_as_now(self, key: str) -> None:
        ...

    def wait_if_needed(self, key: str) -> None:
        ...

    def wait_time_for(self, key: str) -> datetime.timedelta:
        ...

    def next_available_time(self, key: str) -> datetime.datetime:
        ...
