"""Unit tests for the research skill integration."""

import asyncio
from typing import Any

from agents.research.models import NewsItem, ResearchReport, Source
from agents.research.providers import MockNewsProvider, MockSearchProvider
from apps.mission_runner import MissionRunner
from core.memory import InMemoryMemory
from core.skills import SkillRegistry

from apps.mission_runner.run_mission import ResearchSkill


class RecordingMemory(InMemoryMemory):
    async def store(self, key: str, value: Any) -> None:
        self._values[key] = value


def test_research_skill_returns_report_and_persists_it() -> None:
    async def run() -> None:
        source = Source(name="Example source", url="https://example.test")
        registry = SkillRegistry()
        registry.register(ResearchSkill(source_manager=__import__("agents.research.source_manager", fromlist=["SourceManager"]).SourceManager()))
        skill = registry.get("research")
        assert skill is not None

        memory = RecordingMemory()
        report = await skill.execute({"goal": "Research AI news", "memory": memory})
        assert isinstance(report, ResearchReport)
        assert report.topic == "Research AI news"
        assert await memory.retrieve(f"research:reports:{report.id}") == report

    asyncio.run(run())
