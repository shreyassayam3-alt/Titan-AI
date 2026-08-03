"""In-memory implementation of the learning contract."""

from collections.abc import Sequence
from typing import Any

from core.learning.base import Learning


class InMemoryLearning(Learning):
    """Retains completed task outcomes for the lifetime of the instance."""

    def __init__(self) -> None:
        """Create an empty experience collection."""
        self._experiences: list[dict[str, Any]] = []

    async def record_completed_task(self, task: Any, result: Any) -> None:
        """Append a task-result pair to the local experience collection."""
        self._experiences.append({"task": task, "result": result})

    async def retrieve_experience(
        self, query: Any, *, limit: int | None = None
    ) -> Sequence[Any]:
        """Return the latest retained experiences, optionally constrained by ``limit``."""
        experiences = tuple(self._experiences)
        if limit is None:
            return experiences
        return experiences[-limit:] if limit > 0 else ()
