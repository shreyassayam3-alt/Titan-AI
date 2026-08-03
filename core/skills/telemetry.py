"""Structured skill execution logging and telemetry."""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class SkillTelemetry:
    """An immutable telemetry record for a skill runtime lifecycle event."""

    execution_id: str
    skill_name: str
    event_type: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    details: dict[str, Any] = field(default_factory=dict)


class SkillTelemetryLogger:
    """Records telemetry in memory and emits it through Python logging."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Create a telemetry logger using the package logger by default."""
        self._logger = logger or logging.getLogger("titan.skills")
        self._records: list[SkillTelemetry] = []

    def new_execution_id(self) -> str:
        """Create an identifier that correlates an execution's lifecycle records."""
        return str(uuid4())

    def record(
        self, execution_id: str, skill_name: str, event_type: str, **details: Any
    ) -> None:
        """Store and log a structured lifecycle record."""
        telemetry = SkillTelemetry(execution_id, skill_name, event_type, details=details)
        self._records.append(telemetry)
        self._logger.info("skill_event=%s skill=%s execution=%s", event_type, skill_name, execution_id)

    def records(self) -> tuple[SkillTelemetry, ...]:
        """Return recorded telemetry without exposing its mutable backing store."""
        return tuple(self._records)
