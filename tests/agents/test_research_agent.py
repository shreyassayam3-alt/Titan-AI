"""Unit tests for the offline research-agent workflow."""

import asyncio
from typing import Any

from agents.research import ResearchAgent, SourceManager
from agents.research.models import NewsItem, Source
from agents.research.providers import MockNewsProvider, MockSearchProvider
from core.events import InMemoryEventBus
from core.memory import InMemoryMemory
from core.scheduler import Scheduler
from core.scheduler.base import ScheduledCallable


class RecordingScheduler(Scheduler):
    """In-memory scheduler double that exposes scheduled jobs to tests."""

    def __init__(self) -> None:
        """Initialize an empty job collection."""
        self.jobs: list[tuple[str, ScheduledCallable]] = []

    async def schedule_recurring(self, schedule: str, job: ScheduledCallable) -> str:
        """Record a job and return a deterministic test handle."""
        self.jobs.append((schedule, job))
        return "scheduled-job"

    async def cancel(self, job_handle: Any) -> None:
        """Provide the required scheduler contract for tests."""


def test_research_agent_stores_report_and_publishes_event() -> None:
    """Run the offline workflow with injectable mock providers."""
    async def run() -> None:
        source = Source(name="Example source", url="https://example.test")
        manager = SourceManager()
        manager.register(MockNewsProvider(items=(NewsItem(headline="Example", source=source),)))
        manager.register(MockSearchProvider(sources=(source,)))
        memory = InMemoryMemory()
        event_bus = InMemoryEventBus()
        completed_reports: list[object] = []

        async def capture(report: object) -> None:
            completed_reports.append(report)

        event_bus.subscribe("research.completed", capture)
        agent = ResearchAgent(source_manager=manager, memory=memory, event_bus=event_bus)
        report = await agent.research("test topic")

        assert report.news_items[0].headline == "Example"
        assert await memory.retrieve(f"research:reports:{report.id}") == report
        assert completed_reports == [report]

    asyncio.run(run())


def test_research_agent_delegates_recurring_jobs_to_scheduler() -> None:
    """Verify scheduling stays delegated to the scheduler abstraction."""
    async def run() -> None:
        scheduler = RecordingScheduler()
        agent = ResearchAgent(
            source_manager=SourceManager(),
            memory=InMemoryMemory(),
            event_bus=InMemoryEventBus(),
            scheduler=scheduler,
        )
        assert await agent.schedule_recurring("test topic", "daily") == "scheduled-job"
        assert scheduler.jobs[0][0] == "daily"

    asyncio.run(run())
