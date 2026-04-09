import contextlib
import datetime
from collections.abc import Generator, Hashable
from typing import Protocol  # pragma: no cover

Key = Hashable


class ThrottleController(Protocol):  # pragma: no cover
    def cooldown_time_for(self, key: Key) -> datetime.timedelta: ...

    def record_use_time(
        self, key: Key, use_time: datetime.datetime,
    ) -> None: ...

    def record_use_time_as_now(self, key: Key) -> None: ...

    def wait_if_needed(self, key: Key) -> None: ...

    def wait_time_for(self, key: Key) -> datetime.timedelta: ...

    def next_available_time(self, key: Key) -> datetime.datetime: ...

    @contextlib.contextmanager
    def use(self, key: Key) -> Generator[None, None, None]:
        self.wait_if_needed(key)
        self.record_use_time_as_now(key)
        yield
