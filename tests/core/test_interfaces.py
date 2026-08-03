"""Placeholder tests for concrete implementations of core interfaces.

Contract tests will be added once the first implementations are introduced.
"""


def test_core_interface_contracts_placeholder() -> None:
    """Reserve a test location for interface implementation contracts."""
    pass


def test_sprint_two_interfaces_are_importable() -> None:
    """Reserve an import-contract test for the Sprint 2 interfaces."""
    from core import Executor, Learning, Reasoner, Scheduler, ToolRegistry

    assert all((Executor, Learning, Reasoner, Scheduler, ToolRegistry))


def test_in_memory_workflow_executes_goal_and_publishes_events() -> None:
    """Exercise the local Sprint 3 workflow without external dependencies."""
    import asyncio

    from core import (
        Goal,
        InMemoryEventBus,
        InMemoryLearning,
        InMemoryMemory,
        PlaceholderExecutor,
        SimplePlanner,
        SimpleReasoner,
        WorkflowOrchestrator,
    )

    async def run_workflow() -> tuple[object, list[str]]:
        events: list[str] = []
        event_bus = InMemoryEventBus()

        async def record_event(_: object) -> None:
            events.append("completed")

        event_bus.subscribe("goal.completed", record_event)
        workflow = WorkflowOrchestrator(
            planner=SimplePlanner(),
            reasoner=SimpleReasoner(),
            executor=PlaceholderExecutor(),
            learning=InMemoryLearning(),
            memory=InMemoryMemory(),
            event_bus=event_bus,
        )
        report = await workflow.execute(Goal(title="Test goal", description="A local test."))
        return report, events

    report, events = asyncio.run(run_workflow())
    assert report.goal.status == "completed"
    assert report.results
    assert events == ["completed"]
