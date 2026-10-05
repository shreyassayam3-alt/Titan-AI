"""Enhanced planner that decomposes goals into meaningful tasks."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from core.models import Goal, Task
from core.planner.base import Planner


class EnhancedPlanner(Planner):
    """Decomposes goals into multi-step task plans."""

    async def create_plan(self, goal: Any, *, context: Any | None = None) -> Sequence[Task]:
        """Create an execution plan by decomposing the goal."""
        return await self.decompose_goal(goal, context=context)

    async def decompose_goal(self, goal: Any, *, context: Any | None = None) -> Sequence[Task]:
        """Break down a goal into constituent tasks."""
        if not isinstance(goal, Goal):
            raise TypeError("EnhancedPlanner requires a Goal instance.")

        # Extract keywords from goal title for task generation
        keywords = self._extract_keywords(goal.title)
        tasks = []

        # Generate analysis, execution, and reporting tasks
        if keywords:
            # Analysis phase
            tasks.append(
                Task(
                    parent_goal=goal.id,
                    title=f"Analyze: {goal.title}",
                    dependencies=[],
                )
            )

            # Execution phase
            for keyword in keywords:
                tasks.append(
                    Task(
                        parent_goal=goal.id,
                        title=f"Execute: {keyword}",
                        dependencies=[tasks[0].id] if tasks else [],
                    )
                )

            # Reporting phase
            tasks.append(
                Task(
                    parent_goal=goal.id,
                    title=f"Report: {goal.title}",
                    dependencies=[t.id for t in tasks[1:]] if len(tasks) > 1 else [],
                )
            )
        else:
            # Simple fallback
            tasks.append(Task(parent_goal=goal.id, title=goal.title))

        return tuple(tasks)

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract key concepts from goal text."""
        # Simple keyword extraction from goal title
        stop_words = {"the", "a", "an", "and", "or", "is", "for", "to", "of"}
        words = text.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 2][:3]
