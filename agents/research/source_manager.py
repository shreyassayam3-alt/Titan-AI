"""Provider registration and discovery for the research agent."""

from collections.abc import Mapping
from typing import Any

from agents.research.models import NewsItem, Source
from agents.research.providers import MarketProvider, NewsProvider, SearchProvider


class SourceManager:
    """Registry and access point for independently deployable research providers.

    Providers are registered by their stable names and may implement one or more
    provider contracts. This keeps provider selection separate from collection
    and report generation.
    """

    def __init__(self) -> None:
        """Create an empty provider registry."""
        self._providers: dict[str, object] = {}
        self._news_providers: list[NewsProvider] = []
        self._search_providers: list[SearchProvider] = []
        self._market_providers: list[MarketProvider] = []

    def register(self, provider: object) -> None:
        """Register a provider that implements at least one provider contract."""
        if not isinstance(provider, (NewsProvider, SearchProvider, MarketProvider)):
            raise TypeError("Provider must implement a supported research provider interface.")
        if provider.name in self._providers:
            raise ValueError(f"A provider named '{provider.name}' is already registered.")

        self._providers[provider.name] = provider
        if isinstance(provider, NewsProvider):
            self._news_providers.append(provider)
        if isinstance(provider, SearchProvider):
            self._search_providers.append(provider)
        if isinstance(provider, MarketProvider):
            self._market_providers.append(provider)

    def unregister(self, provider_name: str) -> None:
        """Remove a registered provider and all of its supported capabilities."""
        provider = self._providers.pop(provider_name, None)
        if provider is None:
            return
        self._news_providers = [item for item in self._news_providers if item is not provider]
        self._search_providers = [item for item in self._search_providers if item is not provider]
        self._market_providers = [item for item in self._market_providers if item is not provider]

    def provider_names(self) -> tuple[str, ...]:
        """Return the names of all currently registered providers."""
        return tuple(self._providers)

    async def collect_news(self, topic: str) -> tuple[NewsItem, ...]:
        """Collect news from every registered news provider."""
        items: list[NewsItem] = []
        for provider in self._news_providers:
            items.extend(await provider.get_news(topic))
        return tuple(items)

    async def search(self, query: str) -> tuple[Source, ...]:
        """Collect source references from every registered search provider."""
        sources: list[Source] = []
        for provider in self._search_providers:
            sources.extend(await provider.search(query))
        return tuple(sources)

    async def market_data(self, identifier: str) -> Mapping[str, Mapping[str, Any]]:
        """Return data grouped by provider for an explicitly requested identifier."""
        return {
            provider.name: await provider.get_market_data(identifier)
            for provider in self._market_providers
        }
