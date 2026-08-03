"""Goal domain model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class GoalStatus(StrEnum):
    """Lifecycle states for a goal processed by an orchestrator."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


def _new_identifier() -> str:
    """Create a string identifier suitable for an in-memory domain object."""
    return str(uuid4())


def _utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


@dataclass(slots=True)
class Goal:
    """A unit of desired work submitted to the orchestration workflow.

    The model is intentionally transport-agnostic, so it can later be stored
    in a database or received from an API without changing the core contract.
    """

    title: str
    description: str
    priority: int = 0
    id: str = field(default_factory=_new_identifier)
    status: GoalStatus = GoalStatus.PENDING
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)

    def touch(self) -> None:
        """Update the timestamp after a state transition."""
        self.updated_at = _utc_now()
