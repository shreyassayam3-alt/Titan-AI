"""Task domain model."""

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import uuid4


class TaskStatus(StrEnum):
    """Lifecycle states for a task produced from a goal."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


def _new_identifier() -> str:
    """Create a string identifier suitable for an in-memory domain object."""
    return str(uuid4())


@dataclass(slots=True)
class Task:
    """A task belonging to a goal and optionally depending on other tasks."""

    parent_goal: str
    title: str
    id: str = field(default_factory=_new_identifier)
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)
