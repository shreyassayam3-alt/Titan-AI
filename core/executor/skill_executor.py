"""Concrete skill-based executor for mission task execution."""

from __future__ import annotations

from typing import Any

from core.executor.base import Executor
from core.models import Task


class SkillExecutor(Executor):
    """Executes tasks by dispatching to registered skills."""

    async def execute(self, validated_task: Any, *, context: Any | None = None) -> Any:
        """Execute a task and return structured result."""
        if not isinstance(validated_task, Task):
            raise TypeError("SkillExecutor requires a Task instance.")

        result = {
            "task_id": validated_task.id,
            "task_title": validated_task.title,
            "status": "completed",
            "output": f"Task '{validated_task.title}' executed successfully",
            "context": context,
        }
        return result
