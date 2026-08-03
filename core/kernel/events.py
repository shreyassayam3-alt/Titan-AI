"""Persistent-friendly mission lifecycle event logging."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from core.kernel.missions import Mission


@dataclass(frozen=True, slots=True)
class MissionEvent:
    """An immutable record of a mission lifecycle transition."""

    event_type: str
    mission_id: str
    goal_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize this event to JSON-compatible state."""
        return {
            **self.details,
            "event_type": self.event_type,
            "mission_id": self.mission_id,
            "goal_id": self.goal_id,
            "timestamp": self.timestamp.isoformat(),
        }


class EventLogger:
    """Captures every mission lifecycle transition in chronological order."""

    def __init__(self) -> None:
        """Create an empty in-memory event log."""
        self._events: list[MissionEvent] = []

    def log(self, event_type: str, mission: Mission) -> None:
        """Append a lifecycle event for ``mission``."""
        self._events.append(MissionEvent(event_type, mission.id, mission.goal_id))

    def events(self) -> tuple[MissionEvent, ...]:
        """Return all recorded events without exposing mutable storage."""
        return tuple(self._events)

    def snapshot(self) -> list[dict[str, Any]]:
        """Return JSON-compatible event log state."""
        return [event.to_dict() for event in self._events]

    def restore(self, events: list[dict[str, Any]]) -> None:
        """Restore events that were persisted by :meth:`snapshot`."""
        self._events = [
            MissionEvent(
                event_type=str(item["event_type"]),
                mission_id=str(item["mission_id"]),
                goal_id=str(item["goal_id"]),
                timestamp=datetime.fromisoformat(item["timestamp"]),
                details={
                    key: value
                    for key, value in item.items()
                    if key not in {"event_type", "mission_id", "goal_id", "timestamp"}
                },
            )
            for item in events
        ]
