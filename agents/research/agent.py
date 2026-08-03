"""Research-agent orchestration entry point."""

from typing import Any

from agents.research.collector import NewsCollector
from agents.research.models import ResearchReport
from agents.research.report_generator import ReportGenerator
from agents.research.source_manager import SourceManager
from core.events import EventBus
from core.memory import Memory
from core.scheduler import Scheduler


class ResearchAgent:
    """Coordinates offline research collection, report generation, and delivery.

    The agent depends solely on abstractions, allowing provider plugins and core
    infrastructure to be replaced independently in production deployments.
    """

    def __init__(
        self,
        *,
        source_manager: SourceManager,
        memory: Memory,
        event_bus: EventBus,
        scheduler: Scheduler | None = None,
        news_collector: NewsCollector | None = None,
        report_generator: ReportGenerator | None = None,
    ) -> None:
        """Initialize the agent with injected infrastructure and collaborators."""
        self._source_manager = source_manager
        self._memory = memory
        self._event_bus = event_bus
        self._scheduler = scheduler
        self._news_collector = news_collector or NewsCollector(source_manager)
        self._report_generator = report_generator or ReportGenerator()

    async def research(self, topic: str) -> ResearchReport:
        """Collect research material, persist a report, and publish lifecycle events."""
        await self._event_bus.publish("research.started", {"topic": topic})
        try:
            news_items = await self._news_collector.collect(topic)
            discovered_sources = await self._source_manager.search(topic)
            report = self._report_generator.generate(topic, news_items, discovered_sources)
            await self._memory.store(f"research:reports:{report.id}", report)
            await self._event_bus.publish("research.completed", report)
            return report
        except Exception as error:
            await self._event_bus.publish("research.failed", {"topic": topic, "error": error})
            raise

    async def schedule_recurring(self, topic: str, schedule: str) -> Any:
        """Schedule recurring research for ``topic`` through the configured scheduler."""
        if self._scheduler is None:
            raise RuntimeError("A Scheduler is required to schedule recurring research.")

        async def run_research() -> ResearchReport:
            """Execute the recurring research job."""
            return await self.research(topic)

        return await self._scheduler.schedule_recurring(schedule, run_research)
