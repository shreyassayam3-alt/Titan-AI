"""Goal lifecycle management for the central runtime."""

from datetime import datetime
from typing import Any

from core.models import Goal, GoalStatus


class GoalManager:
    """Creates, updates, archives, and reprioritizes in-memory goals."""

    def __init__(self) -> None:
        """Create an empty goal collection."""
        self._goals: dict[str, Goal] = {}

    def create(
        self, title: str, description: str, *, priority: int = 0
    ) -> Goal:
        """Create and retain a new pending goal."""
        goal = Goal(title=title, description=description, priority=priority)
        self._goals[goal.id] = goal
        return goal

    def get(self, goal_id: str) -> Goal | None:
        """Return a goal by identifier, when available."""
        return self._goals.get(goal_id)

    def update(
        self, goal_id: str, *, title: str | None = None, description: str | None = None
    ) -> Goal:
        """Update mutable goal text fields and refresh its timestamp."""
        goal = self._require(goal_id)
        if title is not None:
            goal.title = title
        if description is not None:
            goal.description = description
        goal.touch()
        return goal

    def archive(self, goal_id: str) -> Goal:
        """Archive a goal without deleting its execution history."""
        goal = self._require(goal_id)
        goal.status = GoalStatus.ARCHIVED
        goal.touch()
        return goal

    def prioritize(self, goal_id: str, priority: int) -> Goal:
        """Set a goal's priority for clients that create follow-on missions."""
        goal = self._require(goal_id)
        goal.priority = priority
        goal.touch()
        return goal

    def snapshot(self) -> list[dict[str, Any]]:
        """Return JSON-compatible persistent state for all goals."""
        return [
            {
                "id": goal.id,
                "title": goal.title,
                "description": goal.description,
                "priority": goal.priority,
                "status": goal.status.value,
                "created_at": goal.created_at.isoformat(),
                "updated_at": goal.updated_at.isoformat(),
            }
            for goal in self._goals.values()
        ]

    def restore(self, goals: list[dict[str, Any]]) -> None:
        """Restore previously persisted goals."""
        self._goals = {
            str(item["id"]): Goal(
                id=str(item["id"]),
                title=str(item["title"]),
                description=str(item["description"]),
                priority=int(item["priority"]),
                status=GoalStatus(item["status"]),
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=datetime.fromisoformat(item["updated_at"]),
            )
            for item in goals
        }

    def _require(self, goal_id: str) -> Goal:
        """Return a goal or raise a clear lookup error."""
        goal = self.get(goal_id)
        if goal is None:
            raise KeyError(f"Unknown goal '{goal_id}'.")
        return goal
