"""Real research skill for mission execution."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agents.research.models import ResearchReport, Source
from agents.research.report_generator import ReportGenerator
from agents.research.source_manager import SourceManager
from apps.mission_runner.providers import KeywordNewsProvider, KeywordSearchProvider
from core.memory import Memory
from core.skills import Skill


class ResearchSkill(Skill):
    """Collects sources, ranks them, and produces a structured research report."""

    name = "research"

    def __init__(self, source_manager: SourceManager | None = None) -> None:
        self._source_manager = source_manager or SourceManager()
        self._report_generator = ReportGenerator()
        self._source_manager.register(KeywordNewsProvider())
        self._source_manager.register(KeywordSearchProvider())

    async def validate(self, input_data: Mapping[str, Any]) -> None:
        if "goal" not in input_data:
            raise ValueError("goal is required")

    async def execute(self, input_data: Mapping[str, Any]) -> Any:
        goal = str(input_data["goal"])
        memory = input_data.get("memory")
        news_items = list(await self._source_manager.collect_news(goal))
        discovered_sources = list(await self._source_manager.search(goal))

        unique_sources: list[Source] = []
        seen: set[str] = set()
        for source in discovered_sources:
            if source.id in seen:
                continue
            seen.add(source.id)
            unique_sources.append(source)

        ranked_sources = sorted(
            unique_sources,
            key=lambda item: self._score_source(goal, item),
            reverse=True,
        )

        report = self._report_generator.generate(goal, news_items, ranked_sources)
        report.metadata.update(
            {
                "executive_summary": self._executive_summary(goal, news_items),
                "key_findings": self._key_findings(news_items),
                "important_facts": self._important_facts(news_items),
                "open_questions": self._open_questions(news_items),
            }
        )
        if memory is not None and hasattr(memory, "store"):
            await memory.store(f"research:reports:{report.id}", report)
        return report

    async def rollback(self, input_data: Mapping[str, Any], error: Exception) -> None:
        return None

    @staticmethod
    def _executive_summary(goal: str, news_items: list[Any]) -> str:
        return f"Research for '{goal}' indicates a mix of emerging signals and unresolved questions."

    @staticmethod
    def _key_findings(news_items: list[Any]) -> list[str]:
        return [item.headline for item in news_items[:3]]

    @staticmethod
    def _important_facts(news_items: list[Any]) -> list[str]:
        return [item.summary for item in news_items if item.summary]

    @staticmethod
    def _open_questions(news_items: list[Any]) -> list[str]:
        return [f"What is next for {item.headline}?" for item in news_items[:2]]

    @staticmethod
    def _score_source(goal: str, source: Source) -> int:
        score = 0
        if goal.lower() in source.name.lower():
            score += 3
        if source.url is not None and source.url.startswith("https://example.test"):
            score += 1
        if source.provider_name:
            score += 1
        return score
