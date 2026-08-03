"""Typed models shared by the coordination layer."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class AgentStatus(StrEnum):
    """Availability states used by task assignment."""

    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"


@dataclass(slots=True)
class Agent:
    """A specialized agent available to receive assigned work."""

    name: str
    capabilities: frozenset[str] = frozenset()
    id: str = field(default_factory=lambda: str(uuid4()))
    status: AgentStatus = AgentStatus.AVAILABLE
    assigned_task_ids: set[str] = field(default_factory=set)


@dataclass(frozen=True, slots=True)
class AgentMessage:
    """An immutable message delivered through the shared EventBus."""

    sender_id: str
    recipient_id: str | None
    topic: str
    payload: Any
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class PlanProposal:
    """A proposed plan with a caller-supplied confidence score."""

    agent_id: str
    plan: Any
    confidence: float


@dataclass(frozen=True, slots=True)
class WorkspaceEntry:
    """A versioned value exposed through controlled workspace access."""

    key: str
    value: Any
    owner_id: str
    version: int
