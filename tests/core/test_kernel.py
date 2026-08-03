"""Unit tests for mission scheduling, retry, persistence, and recovery."""

import asyncio
from pathlib import Path

from core.kernel import KernelConfig, MissionStatus, StateManager, TitanKernel


async def _succeed(_: object) -> None:
    """Provide a successful mission handler for kernel tests."""


def test_queue_orders_priority_and_dependencies(tmp_path: Path) -> None:
    """Run high-priority dependency-free work before blocked lower-priority work."""
    async def run() -> None:
        kernel = TitanKernel(state_manager=StateManager(tmp_path / "state.json"), mission_handler=_succeed)
        goal = kernel.goal_manager.create("Goal", "Description")
        dependency = kernel.create_mission(goal.id, "Dependency", priority=1)
        blocked = kernel.create_mission(goal.id, "Blocked", priority=100, dependencies=(dependency.id,))
        ready = kernel.create_mission(goal.id, "Ready", priority=10)
        assert kernel.decision_engine.next_mission(kernel.mission_queue, kernel.config) is ready
        await kernel.worker.run_once()
        assert ready.status is MissionStatus.COMPLETED
        assert kernel.decision_engine.next_mission(kernel.mission_queue, kernel.config) is dependency
        assert blocked.status is MissionStatus.PENDING

    asyncio.run(run())


def test_worker_retries_failed_missions(tmp_path: Path) -> None:
    """Requeue a mission once and complete it when its later attempt succeeds."""
    async def run() -> None:
        attempts = 0

        async def flaky(_: object) -> None:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise RuntimeError("temporary failure")

        kernel = TitanKernel(state_manager=StateManager(tmp_path / "state.json"), mission_handler=flaky)
        goal = kernel.goal_manager.create("Goal", "Description")
        mission = kernel.create_mission(goal.id, "Retry", max_retries=1)
        await kernel.worker.run_once()
        assert mission.status is MissionStatus.PENDING
        await kernel.worker.run_once()
        assert mission.status is MissionStatus.COMPLETED
        assert mission.attempts == 2

    asyncio.run(run())


def test_persistence_and_recovery_requeues_interrupted_work(tmp_path: Path) -> None:
    """Restore a running mission as pending after a simulated process restart."""
    async def run() -> None:
        path = tmp_path / "state.json"
        first_kernel = TitanKernel(state_manager=StateManager(path), mission_handler=_succeed)
        goal = first_kernel.goal_manager.create("Goal", "Description")
        mission = first_kernel.create_mission(goal.id, "Recover")
        first_kernel.mission_queue.mark_running(mission.id)
        first_kernel.persist()

        recovered_kernel = TitanKernel(state_manager=StateManager(path), mission_handler=_succeed)
        recovered = recovered_kernel.mission_queue.get(mission.id)
        assert recovered is not None
        assert recovered.status is MissionStatus.PENDING
        assert recovered_kernel.goal_manager.get(goal.id) is not None

    asyncio.run(run())
