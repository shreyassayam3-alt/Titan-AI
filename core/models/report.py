"""Execution report model returned by the orchestration workflow."""

from dataclasses import dataclass
from typing import Any

from core.models.goal import Goal
from core.models.task import Task


@dataclass(frozen=True, slots=True)
class ExecutionReport:
    """Summarizes a completed orchestration attempt and its task results."""

    goal: Goal
    tasks: tuple[Task, ...]
    results: tuple[Any, ...]
    strategy: Any | None
