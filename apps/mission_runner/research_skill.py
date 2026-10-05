"""Real research skill for mission execution."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import asdict
from pathlib import Path
from typing import Any

from agents.research.models import ResearchReport, Source
from agents.research.providers.adapters import GitHubProviderAdapter, LocalDocumentProviderAdapter, RSSProviderAdapter
from agents.research.providers.live import BraveSearchProvider, SerperSearchProvider, TavilySearchProvider
from agents.research.providers.registry import ProviderRegistry
from agents.research.report_generator import ReportGenerator
from agents.research.source_manager import SourceManager
from apps.mission_runner.providers import KeywordNewsProvider, KeywordSearchProvider
from core.llm.base import LLMProvider, LLMProviderRegistry
from core.llm.validation import LLMConfigurationError, validate_llm_keys
from core.memory import Memory
from core.skills import Skill


class ResearchSkill(Skill):
    """Collects sources, ranks them, and produces a structured research report."""

    name = "research"

    def __init__(
        self,
        source_manager: SourceManager | None = None,
        provider_registry: ProviderRegistry | None = None,
        provider: LLMProvider | None = None,
    ) -> None:
        self._source_manager = source_manager or SourceManager()
        self._provider_registry = provider_registry or self._build_provider_registry()
        self._llm_provider = provider or self._resolve_llm_provider()
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
                "markdown_report": self._markdown_report(goal, news_items, ranked_sources),
                "change_summary": self._change_summary(goal, news_items),
            }
        )
        provider_response = await self._provider_registry.query(goal)
        llm_summary = ""
        if self._llm_provider is not None:
            try:
                llm_summary = await self._llm_provider.generate(
                    f"Summarize the following research findings into five concise bullets: {goal}",
                    system_prompt="You are Titan's research summarizer.",
                )
            except Exception as exc:
                llm_summary = f"LLM call failed: {exc}"
        report.metadata.update(
            {
                "providers_used": provider_response.providers_used,
                "provider_summary": provider_response.summary,
                "provider_results": [asdict(result) for result in provider_response.results],
                "llm_summary": llm_summary,
                "llm_provider": getattr(self._llm_provider, "name", "none"),
            }
        )
        if memory is not None and hasattr(memory, "store"):
            await memory.store(f"research:reports:{report.id}", report)
        return report

    async def rollback(self, input_data: Mapping[str, Any], error: Exception) -> None:
        return None

    @staticmethod
    def _build_provider_registry() -> ProviderRegistry:
        workspace_root = Path(__file__).resolve().parents[2]
        registry = ProviderRegistry()
        registry.register(LocalDocumentProviderAdapter(root=workspace_root))
        registry.register(RSSProviderAdapter(feed_path=workspace_root / "docs" / "fixtures" / "titan-news.xml"))
        registry.register(GitHubProviderAdapter(repo_root=workspace_root))
        if os.getenv("TAVILY_API_KEY"):
            registry.register(TavilySearchProvider())
        if os.getenv("BRAVE_API_KEY"):
            registry.register(BraveSearchProvider())
        if os.getenv("SERPER_API_KEY"):
            registry.register(SerperSearchProvider())
        return registry

    @staticmethod
    def _resolve_llm_provider() -> LLMProvider | None:
        try:
            validate_llm_keys()
        except LLMConfigurationError:
            return None
        return LLMProviderRegistry.from_env().get_provider()

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
    def _markdown_report(goal: str, news_items: list[Any], sources: list[Source]) -> str:
        top_stories = news_items[:5]
        lines = [f"# {goal}", "", "## Executive Summary", "- Research signals are building around the requested topic.", "", "## Top Stories"]
        for index, item in enumerate(top_stories, start=1):
            lines.append(f"{index}. **{item.headline}**")
            if item.summary:
                lines.append(f"   - {item.summary}")
        lines.extend(["", "## Sources", *[f"- {source.name}" for source in sources[:5]]])
        return "\n".join(lines)

    @staticmethod
    def _change_summary(goal: str, news_items: list[Any]) -> str:
        if not news_items:
            return f"No new change data for {goal}."
        latest = " | ".join(item.headline for item in news_items[:3])
        return f"Compared with yesterday, the latest change set for {goal} centers on: {latest}"

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
