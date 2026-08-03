"""Unit tests for skill registration, execution, permissions, and failure handling."""

import asyncio
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from core.kernel import ApprovalPolicy, StateManager, TitanKernel
from core.skills import PermissionManager, PluginLoader, Skill, SkillRegistry, SkillRuntime, SkillStatus


class EchoSkill(Skill):
    """Simple local skill used to exercise the runtime contract."""

    name = "echo"
    rollback_called = False

    async def validate(self, input_data: Mapping[str, Any]) -> None:
        """Require the payload expected by this test skill."""
        if "value" not in input_data:
            raise ValueError("value is required")

    async def execute(self, input_data: Mapping[str, Any]) -> Any:
        """Return the supplied test value."""
        return input_data["value"]

    async def rollback(self, input_data: Mapping[str, Any], error: Exception) -> None:
        """Record rollback for failure assertions."""
        type(self).rollback_called = True


class FailingSkill(EchoSkill):
    """Skill that fails after validation so rollback can be verified."""

    name = "failing"

    async def execute(self, input_data: Mapping[str, Any]) -> Any:
        """Raise a controlled failure."""
        raise RuntimeError("execution failed")


class SensitiveSkill(EchoSkill):
    """Skill that requires explicit approval under restrictive policy."""

    name = "sensitive"
    sensitive = True


def test_registry_discovers_concrete_skill_classes() -> None:
    """Discover and register classes provided by a loaded module."""
    registry = SkillRegistry()
    discovered = registry.discover(sys.modules[__name__])
    assert {"echo", "failing", "sensitive"}.issubset(discovered)


def test_runtime_executes_and_reports_results() -> None:
    """Execute a registered skill and deliver its result to a reporter."""
    async def run() -> None:
        registry = SkillRegistry()
        registry.register(EchoSkill())
        reported: list[object] = []
        runtime = SkillRuntime(
            registry,
            PermissionManager(),
            result_reporter=lambda result: reported.append(result),
        )
        result = await runtime.execute("echo", {"value": "ok"})
        assert result.status is SkillStatus.COMPLETED
        assert result.output == "ok"
        assert reported == [result]

    asyncio.run(run())


def test_runtime_denies_unapproved_sensitive_skill() -> None:
    """Block sensitive work until its explicit approval is granted."""
    async def run() -> None:
        registry = SkillRegistry()
        registry.register(SensitiveSkill())
        permissions = PermissionManager(ApprovalPolicy.REQUIRE_APPROVAL)
        runtime = SkillRuntime(registry, permissions)
        assert (await runtime.execute("sensitive", {"value": "ok"})).status is SkillStatus.DENIED
        permissions.approve("sensitive")
        assert (await runtime.execute("sensitive", {"value": "ok"})).status is SkillStatus.COMPLETED

    asyncio.run(run())


def test_runtime_rolls_back_execution_failures() -> None:
    """Run rollback after an execution error and report failure."""
    async def run() -> None:
        FailingSkill.rollback_called = False
        registry = SkillRegistry()
        registry.register(FailingSkill())
        result = await SkillRuntime(registry, PermissionManager()).execute("failing", {"value": "ok"})
        assert result.status is SkillStatus.FAILED
        assert FailingSkill.rollback_called

    asyncio.run(run())


def test_runtime_reports_results_to_kernel(tmp_path: Path) -> None:
    """Persist skill runtime outcomes through the kernel reporting callback."""
    async def mission_handler(_: object) -> None:
        """Provide the required kernel mission handler for this integration test."""

    async def run() -> None:
        kernel = TitanKernel(
            state_manager=StateManager(tmp_path / "state.json"),
            mission_handler=mission_handler,
        )
        registry = SkillRegistry()
        registry.register(EchoSkill())
        result = await SkillRuntime(
            registry,
            PermissionManager(),
            result_reporter=kernel.record_skill_result,
        ).execute("echo", {"value": "stored"})
        assert kernel.skill_results() == (result,)

    asyncio.run(run())


def test_plugin_loader_discovers_skills_without_kernel_changes(tmp_path: Path) -> None:
    """Load a plugin skill from a temporary module directory."""
    plugin_path = tmp_path / "sample_skill.py"
    plugin_path.write_text(
        "from core.skills import Skill\n"
        "class PluginSkill(Skill):\n"
        "    name = 'plugin'\n"
        "    async def validate(self, input_data): pass\n"
        "    async def execute(self, input_data): return None\n"
        "    async def rollback(self, input_data, error): pass\n",
        encoding="utf-8",
    )
    registry = SkillRegistry()
    assert PluginLoader(registry).load_directory(tmp_path) == ("plugin",)
    assert registry.get("plugin") is not None
