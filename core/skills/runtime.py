"""Permission-aware execution runtime for registered skills."""

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from core.skills.permissions import PermissionManager
from core.skills.registry import SkillRegistry
from core.skills.telemetry import SkillTelemetryLogger

type ResultReporter = Callable[["SkillExecutionResult"], Awaitable[None] | None]


class SkillStatus(StrEnum):
    """Terminal states reported by the skill runtime."""

    COMPLETED = "completed"
    FAILED = "failed"
    DENIED = "denied"


@dataclass(frozen=True, slots=True)
class SkillExecutionResult:
    """Outcome reported to callers and optionally persisted by the kernel."""

    execution_id: str
    skill_name: str
    status: SkillStatus
    output: Any | None = None
    error: str | None = None
    completed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


class SkillRuntime:
    """Executes registered skills with validation, permission, rollback, and telemetry.

    A result reporter may be bound to ``TitanKernel.record_skill_result`` or
    another persistence adapter, keeping the runtime independent of the kernel.
    """

    def __init__(
        self,
        registry: SkillRegistry,
        permissions: PermissionManager,
        telemetry: SkillTelemetryLogger | None = None,
        result_reporter: ResultReporter | None = None,
    ) -> None:
        """Initialize the runtime with injected policy and reporting collaborators."""
        self._registry = registry
        self._permissions = permissions
        self._telemetry = telemetry or SkillTelemetryLogger()
        self._result_reporter = result_reporter

    async def execute(
        self, skill_name: str, input_data: Mapping[str, Any]
    ) -> SkillExecutionResult:
        """Run one skill lifecycle and return a terminal execution result."""
        skill = self._registry.get(skill_name)
        if skill is None:
            raise KeyError(f"Unknown skill '{skill_name}'.")

        execution_id = self._telemetry.new_execution_id()
        self._telemetry.record(execution_id, skill.name, "skill.started")
        try:
            self._permissions.require(skill)
        except PermissionError as error:
            result = SkillExecutionResult(execution_id, skill.name, SkillStatus.DENIED, error=str(error))
            self._telemetry.record(execution_id, skill.name, "skill.denied", error=str(error))
            await self._report(result)
            return result

        try:
            await skill.validate(input_data)
            output = await skill.execute(input_data)
        except Exception as error:
            self._telemetry.record(execution_id, skill.name, "skill.failed", error=str(error))
            try:
                await skill.rollback(input_data, error)
            except Exception as rollback_error:
                self._telemetry.record(
                    execution_id, skill.name, "skill.rollback_failed", error=str(rollback_error)
                )
            else:
                self._telemetry.record(execution_id, skill.name, "skill.rolled_back")
            result = SkillExecutionResult(execution_id, skill.name, SkillStatus.FAILED, error=str(error))
        else:
            result = SkillExecutionResult(execution_id, skill.name, SkillStatus.COMPLETED, output=output)
            self._telemetry.record(execution_id, skill.name, "skill.completed")
        await self._report(result)
        return result

    async def _report(self, result: SkillExecutionResult) -> None:
        """Deliver a result to the optional kernel-facing reporting adapter."""
        if self._result_reporter is None:
            return
        reporting_result = self._result_reporter(result)
        if isinstance(reporting_result, Awaitable):
            await reporting_result
