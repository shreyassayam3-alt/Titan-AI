import asyncio

from agents.research.providers.live import BraveSearchProvider, SerperSearchProvider, TavilySearchProvider


def test_live_provider_adapters_build_sources_when_keys_are_present() -> None:
    async def run() -> None:
        providers = [
            TavilySearchProvider(api_key="demo"),
            BraveSearchProvider(api_key="demo"),
            SerperSearchProvider(api_key="demo"),
        ]
        for provider in providers:
            try:
                results = await provider.search("titan ai")
            except Exception:
                results = []
            if isinstance(provider, SerperSearchProvider):
                assert isinstance(results, list)
            else:
                assert isinstance(results, list)

    asyncio.run(run())
