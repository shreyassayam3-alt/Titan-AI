import asyncio
from pathlib import Path

from apps.mission_runner.provider_demo import run_provider_demo
from agents.research.providers.registry import ProviderRegistry
from agents.research.providers.adapters import GitHubProviderAdapter, LocalDocumentProviderAdapter, RSSProviderAdapter


def test_provider_registry_merges_and_ranks_results() -> None:
    async def run() -> None:
        workspace_root = Path(__file__).resolve().parents[2]
        registry = ProviderRegistry()
        registry.register(LocalDocumentProviderAdapter(root=workspace_root))
        registry.register(RSSProviderAdapter(feed_path=workspace_root / "docs" / "fixtures" / "titan-news.xml"))
        registry.register(GitHubProviderAdapter(repo_root=workspace_root))

        response = await registry.query("provider framework")

        assert response.results
        assert len(response.results) >= 3
        assert response.results[0].confidence >= response.results[-1].confidence
        assert any(result.provider_name == "local-documents" for result in response.results)
        assert any(result.provider_name == "rss" for result in response.results)

    asyncio.run(run())


def test_provider_demo_returns_normalized_response() -> None:
    async def run() -> None:
        response = await run_provider_demo("titan provider framework")
        assert response.results
        assert response.summary
        assert response.providers_used

    asyncio.run(run())
