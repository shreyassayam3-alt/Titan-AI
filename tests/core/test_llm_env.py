import asyncio

from apps.mission_runner.research_skill import ResearchSkill


def test_research_skill_handles_missing_llm_keys_gracefully() -> None:
    async def run() -> None:
        skill = ResearchSkill()
        report = await skill.execute({"goal": "Explain quantum computing in simple words."})
        assert report.metadata["llm_provider"] in {"none", "mock"}

    asyncio.run(run())
