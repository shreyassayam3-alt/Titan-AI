"""Immutable models exchanged by the decision engine and integrations."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class DecisionContext:
    """Inputs used to evaluate a set of candidate actions.

    Actions remain domain-neutral so the same engine can evaluate missions,
    skills, workflows, or application-level commands.
    """

    actions: tuple[Any, ...]
    metadata: dict[str, Any] = field(default_factory=dict)
    correlation_id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True, slots=True)
class DecisionResult:
    """The selected action and transparent per-action evaluation details."""

    context_id: str
    selected_action: Any | None
    scores: tuple[float | None, ...]
    evaluations: tuple[dict[str, float | bool], ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
