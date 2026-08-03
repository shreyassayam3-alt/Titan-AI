"""Abstract contract for managing recurring jobs."""

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import Any

type ScheduledCallable = Callable[[], Awaitable[Any]]


class Scheduler(ABC):
    """Schedules and cancels recurring asynchronous jobs.

    Concrete schedulers define the accepted recurrence expression and the
    returned job-handle representation.
    """

    @abstractmethod
    async def schedule_recurring(self, schedule: str, job: ScheduledCallable) -> Any:
        """Schedule ``job`` according to ``schedule`` and return a job handle."""
        ...

    @abstractmethod
    async def cancel(self, job_handle: Any) -> None:
        """Cancel the recurring job identified by ``job_handle``."""
        ...
