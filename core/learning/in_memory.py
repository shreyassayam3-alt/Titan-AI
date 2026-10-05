"""In-memory implementation of the learning contract."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from core.learning.base import Learning


class InMemoryLearning(Learning):
    """Retains task outcomes for the lifetime of the instance."""

    def __init__(self) -> None:
        """Create an empty experience collection."""
        self._experiences: list[dict[str, Any]] = []
        self._failures: list[dict[str, Any]] = []

    async def record_completed_task(self, task: Any, result: Any) -> None:
        """Append a task-result pair to the local experience collection."""
        self._experiences.append({
            "task": task,
            "result": result,
            "outcome": "completed",
        })

    async def record_failed_task(self, task: Any, error: Exception) -> None:
        """Record a failed task and the associated error."""
        self._failures.append({
            "task": task,
            "error": str(error),
            "outcome": "failed",
        })

    async def retrieve_experience(
        self, query: Any, *, limit: int | None = None
    ) -> Sequence[Any]:
        """Return the latest experiences relevant to the provided query."""
        matches: list[Any] = []
        for item in self._experiences:
            task = item.get("task")
            if task is None:
                continue
            task_repr = str(task)
            query_repr = str(query)
            if query_repr in task_repr or (hasattr(task, "title") and query_repr in str(task.title)):
                matches.append(item)

        if limit is not None:
            return tuple(matches[-limit:] if limit > 0 else ())
        return tuple(matches)

    async def retrieve_failures(self, *, limit: int | None = None) -> Sequence[Any]:
        """Return recent failures for analysis and optimization."""
        failures = tuple(self._failures)
        if limit is not None:
            return failures[-limit:] if limit > 0 else ()
        return failures
