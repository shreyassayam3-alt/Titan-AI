import asyncio

from core.llm import LLMProviderRegistry, LLMProvider
from core.reasoner.llm import LLMReasoner
from apps.mission_runner.research_skill import ResearchSkill


class StubLLMProvider(LLMProvider):
    name = "stub"

    async def generate(self, prompt: str, *, system_prompt: str | None = None, model: str | None = None) -> str:
        return f"stub:{prompt[:20]}"


def test_provider_registry_prefers_configured_provider() -> None:
    registry = LLMProviderRegistry.from_env({"OPENAI_API_KEY": "abc"})
    provider = registry.get_provider()
    assert provider is not None
    assert provider.name == "openai"


def test_llm_reasoner_uses_selected_provider() -> None:
    async def run() -> None:
        reasoner = LLMReasoner(provider=StubLLMProvider())
        response = await reasoner.select_strategy(["alpha", "beta"], context={"goal": "test"})
        assert response == "stub:alpha"

    asyncio.run(run())


def test_openai_provider_uses_real_api_client(monkeypatch) -> None:
    async def run() -> None:
        import core.llm.openai as openai_module

        seen: dict[str, str] = {}

        class FakeResponse:
            output_text = "real openai completion"

        class FakeOpenAI:
            def __init__(self, api_key: str) -> None:
                seen["api_key"] = api_key

            def responses(self):
                class ResponseFactory:
                    def create(self, **kwargs):
                        seen["model"] = kwargs["model"]
                        seen["input"] = kwargs["input"]
                        seen["system"] = kwargs["instructions"]
                        return FakeResponse()

                return ResponseFactory()

        monkeypatch.setattr(openai_module, "OpenAI", FakeOpenAI)
        provider = openai_module.OpenAIProvider(api_key="secret-key")
        response = await provider.generate("Summarize this", system_prompt="You are Titan", model="gpt-4o-mini")

        assert response == "real openai completion"
        assert seen["api_key"] == "secret-key"
        assert seen["model"] == "gpt-4o-mini"
        assert seen["system"] == "You are Titan"

    asyncio.run(run())


def test_research_skill_can_emit_llm_summary() -> None:
    async def run() -> None:
        skill = ResearchSkill(provider=StubLLMProvider())
        report = await skill.execute({"goal": "Research AI news"})
        assert report.metadata["llm_summary"].startswith("stub:")

    asyncio.run(run())
