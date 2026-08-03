"""Mission planning adapter built on the existing planner contract."""

from typing import Any

from core.models import Goal, Task
from core.planner import Planner


class MissionPlanner:
    """Decomposes goals into executable tasks through an injected planner."""

    def __init__(self, planner: Planner) -> None:
        """Initialize the adapter with the application's task planner."""
        self._planner = planner

    async def decompose(self, goal: Goal, *, context: Any | None = None) -> tuple[Task, ...]:
        """Return validated task objects produced for ``goal``."""
        tasks = tuple(await self._planner.decompose_goal(goal, context=context))
        if not all(isinstance(task, Task) for task in tasks):
            raise TypeError("Mission planner requires Task instances from its planner.")
        return tasks
