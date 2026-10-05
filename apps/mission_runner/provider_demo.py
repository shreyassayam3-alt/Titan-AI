from __future__ import annotations

from pathlib import Path

from agents.research.providers.registry import ProviderRegistry
from agents.research.providers.adapters import GitHubProviderAdapter, LocalDocumentProviderAdapter, RSSProviderAdapter


async def run_provider_demo(query: str) -> object:
    workspace_root = Path(__file__).resolve().parents[2]
    registry = ProviderRegistry()
    registry.register(LocalDocumentProviderAdapter(root=workspace_root))
    registry.register(RSSProviderAdapter(feed_path=workspace_root / "docs" / "fixtures" / "titan-news.xml"))
    registry.register(GitHubProviderAdapter(repo_root=workspace_root))
    return await registry.query(query)
