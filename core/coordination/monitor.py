"""Progress monitoring and stall-triggered replanning hooks."""

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

from core.models import Task, TaskStatus

type ReplanHandler = Callable[[Task], Awaitable[None]]


class MissionMonitor:
    """Tracks task observations and requests replanning for stalled work."""

    def __init__(
        self, stall_timeout: timedelta, replan_handler: ReplanHandler
    ) -> None:
        """Initialize a monitor with explicit stall policy and replan callback."""
        self._stall_timeout = stall_timeout
        self._replan_handler = replan_handler
        self._last_progress: dict[str, datetime] = {}

    def record_progress(self, task: Task, *, observed_at: datetime | None = None) -> None:
        """Record the latest observed progress for a task."""
        self._last_progress[task.id] = observed_at or datetime.now(UTC)

    async def inspect(self, tasks: tuple[Task, ...], *, now: datetime | None = None) -> tuple[Task, ...]:
        """Trigger replanning for active tasks whose progress is overdue."""
        current_time = now or datetime.now(UTC)
        stalled: list[Task] = []
        for task in tasks:
            last_progress = self._last_progress.get(task.id)
            if task.status is TaskStatus.IN_PROGRESS and last_progress is not None:
                if current_time - last_progress > self._stall_timeout:
                    await self._replan_handler(task)
                    stalled.append(task)
        return tuple(stalled)
