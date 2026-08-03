"""Unit tests for multi-agent coordination services."""

import asyncio
from datetime import UTC, datetime, timedelta

from core.coordination import (
    AgentCommunicationLayer,
    AgentManager,
    ConflictResolver,
    MissionMonitor,
    SharedWorkspace,
    TaskAssignmentEngine,
)
from core.coordination.models import AgentMessage, PlanProposal
from core.events import InMemoryEventBus
from core.models import Task, TaskStatus


def test_assignment_workspace_and_conflict_resolution() -> None:
    """Route capable work, collaborate with access control, and resolve plans."""
    manager = AgentManager()
    capable = manager.create("planner", capabilities=frozenset({"planning"}))
    manager.create("generalist")
    task = Task(parent_goal="goal", title="Plan")
    assert TaskAssignmentEngine(manager).assign(task, required_capabilities=frozenset({"planning"})) is capable

    workspace = SharedWorkspace()
    workspace.put("plan", {"version": 1}, actor_id=capable.id)
    workspace.grant("plan", owner_id=capable.id, agent_id="reviewer", write=True)
    assert workspace.get("plan", actor_id="reviewer") is not None
    assert ConflictResolver().resolve((PlanProposal("a", "first", 0.5), PlanProposal("b", "second", 0.8))).plan == "second"


def test_communication_and_stall_monitoring() -> None:
    """Deliver EventBus messages and trigger replanning for a stalled task."""
    async def run() -> None:
        bus = InMemoryEventBus()
        received: list[AgentMessage] = []
        communication = AgentCommunicationLayer(bus)

        async def receive(message: AgentMessage) -> None:
            received.append(message)

        communication.subscribe("agent", receive)
        await communication.send(AgentMessage("sender", "agent", "status", {"ok": True}))
        assert len(received) == 1

        replanned: list[Task] = []

        async def replan(task: Task) -> None:
            replanned.append(task)

        task = Task(parent_goal="goal", title="Work", status=TaskStatus.IN_PROGRESS)
        monitor = MissionMonitor(timedelta(seconds=1), replan)
        observed = datetime.now(UTC) - timedelta(seconds=2)
        monitor.record_progress(task, observed_at=observed)
        assert await monitor.inspect((task,), now=datetime.now(UTC)) == (task,)
        assert replanned == [task]

    asyncio.run(run())
