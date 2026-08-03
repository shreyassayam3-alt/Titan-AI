"""Mission model and priority/dependency-aware queue."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Protocol
from uuid import uuid4


class MissionStatus(StrEnum):
    """Lifecycle states for a mission managed by the Titan Kernel."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class MissionEventSink(Protocol):
    """Structural contract for components that record mission transitions."""

    def log(self, event_type: str, mission: "Mission") -> None:
        """Record a lifecycle transition for ``mission``."""
        ...


def _utc_now() -> datetime:
    """Return a timezone-aware timestamp for runtime state changes."""
    return datetime.now(UTC)


@dataclass(slots=True)
class Mission:
    """A scheduled unit of work associated with a goal."""

    goal_id: str
    title: str
    priority: int = 0
    dependencies: tuple[str, ...] = ()
    max_retries: int = 0
    deadline: datetime | None = None
    approved: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))
    status: MissionStatus = MissionStatus.PENDING
    attempts: int = 0
    created_at: datetime = field(default_factory=_utc_now)
    last_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize this mission into JSON-compatible execution state."""
        return {
            "id": self.id,
            "goal_id": self.goal_id,
            "title": self.title,
            "priority": self.priority,
            "dependencies": list(self.dependencies),
            "max_retries": self.max_retries,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "approved": self.approved,
            "status": self.status.value,
            "attempts": self.attempts,
            "created_at": self.created_at.isoformat(),
            "last_error": self.last_error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Mission":
        """Restore a mission previously produced by :meth:`to_dict`."""
        deadline = data.get("deadline")
        return cls(
            id=str(data["id"]),
            goal_id=str(data["goal_id"]),
            title=str(data["title"]),
            priority=int(data["priority"]),
            dependencies=tuple(str(item) for item in data.get("dependencies", ())),
            max_retries=int(data.get("max_retries", 0)),
            deadline=datetime.fromisoformat(deadline) if deadline else None,
            approved=bool(data.get("approved", True)),
            status=MissionStatus(data.get("status", MissionStatus.PENDING)),
            attempts=int(data.get("attempts", 0)),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_error=data.get("last_error"),
        )


class MissionQueue:
    """Maintains missions and their lifecycle transitions in memory."""

    def __init__(self, event_logger: MissionEventSink | None = None) -> None:
        """Create an empty queue with an optional lifecycle event logger."""
        self._missions: dict[str, Mission] = {}
        self._event_logger = event_logger

    def enqueue(self, mission: Mission) -> None:
        """Add a new mission to the queue."""
        if mission.id in self._missions:
            raise ValueError(f"Mission '{mission.id}' already exists.")
        self._missions[mission.id] = mission
        self._log("mission.enqueued", mission)

    def get(self, mission_id: str) -> Mission | None:
        """Return a mission by identifier, when it exists."""
        return self._missions.get(mission_id)

    def approve(self, mission_id: str) -> None:
        """Mark a queued mission as approved for approval-gated execution."""
        mission = self._require(mission_id)
        mission.approved = True
        self._log("mission.approved", mission)

    def executable(
        self, *, require_approval: bool, now: datetime | None = None
    ) -> tuple[Mission, ...]:
        """Return pending missions whose dependencies and deadline permit execution."""
        current_time = now or _utc_now()
        ready: list[Mission] = []
        for mission in self._missions.values():
            if mission.status is not MissionStatus.PENDING:
                continue
            if mission.deadline is not None and mission.deadline < current_time:
                mission.status = MissionStatus.EXPIRED
                self._log("mission.expired", mission)
                continue
            if require_approval and not mission.approved:
                continue
            if all(
                (dependency := self._missions.get(item)) is not None
                and dependency.status is MissionStatus.COMPLETED
                for item in mission.dependencies
            ):
                ready.append(mission)
        return tuple(
            sorted(
                ready,
                key=lambda item: (
                    -item.priority,
                    item.deadline or datetime.max.replace(tzinfo=UTC),
                    item.created_at,
                ),
            )
        )

    def mark_running(self, mission_id: str) -> Mission:
        """Transition an executable mission to running and increment its attempt count."""
        mission = self._require(mission_id)
        mission.status = MissionStatus.RUNNING
        mission.attempts += 1
        self._log("mission.started", mission)
        return mission

    def complete(self, mission_id: str) -> Mission:
        """Mark a running mission as successfully completed."""
        mission = self._require(mission_id)
        mission.status = MissionStatus.COMPLETED
        mission.last_error = None
        self._log("mission.completed", mission)
        return mission

    def fail(self, mission_id: str, error: Exception) -> Mission:
        """Record failure and requeue the mission when its retry budget remains."""
        mission = self._require(mission_id)
        mission.last_error = str(error)
        if mission.attempts <= mission.max_retries:
            mission.status = MissionStatus.PENDING
            self._log("mission.retry_scheduled", mission)
        else:
            mission.status = MissionStatus.FAILED
            self._log("mission.failed", mission)
        return mission

    def snapshot(self) -> list[dict[str, Any]]:
        """Return JSON-compatible state for all queued missions."""
        return [mission.to_dict() for mission in self._missions.values()]

    def restore(self, missions: list[dict[str, Any]]) -> None:
        """Restore queue state and make interrupted running missions retryable."""
        self._missions = {
            mission.id: mission
            for item in missions
            for mission in (Mission.from_dict(item),)
        }
        for mission in self._missions.values():
            if mission.status is MissionStatus.RUNNING:
                mission.status = MissionStatus.PENDING
                self._log("mission.recovered", mission)

    def _require(self, mission_id: str) -> Mission:
        """Return an existing mission or raise a clear lookup error."""
        mission = self.get(mission_id)
        if mission is None:
            raise KeyError(f"Unknown mission '{mission_id}'.")
        return mission

    def _log(self, event_type: str, mission: Mission) -> None:
        """Log a lifecycle transition when logging is configured."""
        if self._event_logger is not None:
            self._event_logger.log(event_type, mission)
