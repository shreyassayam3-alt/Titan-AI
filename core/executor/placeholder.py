"""Placeholder executor for local orchestration workflows."""

from typing import Any

from core.executor.base import Executor
from core.models import Task


class PlaceholderExecutor(Executor):
    """Returns a deterministic result without performing external work."""

    async def execute(self, validated_task: Any, *, context: Any | None = None) -> Any:
        """Return a descriptive result for a validated ``Task`` placeholder."""
        if not isinstance(validated_task, Task):
            raise TypeError("PlaceholderExecutor requires a Task instance.")
        return {"task_id": validated_task.id, "status": "completed"}
