"""Minimal planner implementation for the first execution workflow."""

from collections.abc import Sequence
from typing import Any

from core.models import Goal, Task
from core.planner.base import Planner


class SimplePlanner(Planner):
    """Creates one executable placeholder task for each submitted goal."""

    async def create_plan(self, goal: Any, *, context: Any | None = None) -> Sequence[Task]:
        """Return the minimal task plan created from ``goal``."""
        return await self.decompose_goal(goal, context=context)

    async def decompose_goal(self, goal: Any, *, context: Any | None = None) -> Sequence[Task]:
        """Represent ``goal`` as a single independent placeholder task."""
        if not isinstance(goal, Goal):
            raise TypeError("SimplePlanner requires a Goal instance.")
        return (Task(parent_goal=goal.id, title=goal.title),)
