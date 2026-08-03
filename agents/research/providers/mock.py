"""Offline provider implementations used by tests and local development."""

from collections.abc import Mapping, Sequence
from typing import Any

from agents.research.models import NewsItem, Source
from agents.research.providers.base import MarketProvider, NewsProvider, SearchProvider


class MockNewsProvider(NewsProvider):
    """Returns configured news items without contacting an external service."""

    def __init__(self, name: str = "mock-news", items: Sequence[NewsItem] = ()) -> None:
        """Configure this mock provider with static ``items``."""
        self._name = name
        self._items = tuple(items)

    @property
    def name(self) -> str:
        """Return this mock provider's registration name."""
        return self._name

    async def get_news(self, topic: str) -> Sequence[NewsItem]:
        """Return the configured items for every topic."""
        return self._items


class MockSearchProvider(SearchProvider):
    """Returns configured sources without contacting an external service."""

    def __init__(self, name: str = "mock-search", sources: Sequence[Source] = ()) -> None:
        """Configure this mock provider with static ``sources``."""
        self._name = name
        self._sources = tuple(sources)

    @property
    def name(self) -> str:
        """Return this mock provider's registration name."""
        return self._name

    async def search(self, query: str) -> Sequence[Source]:
        """Return the configured sources for every query."""
        return self._sources


class MockMarketProvider(MarketProvider):
    """Returns configured market data without contacting an external service."""

    def __init__(self, name: str = "mock-market", data: Mapping[str, Any] | None = None) -> None:
        """Configure this mock provider with static ``data``."""
        self._name = name
        self._data = dict(data or {})

    @property
    def name(self) -> str:
        """Return this mock provider's registration name."""
        return self._name

    async def get_market_data(self, identifier: str) -> Mapping[str, Any]:
        """Return a copy of the configured market-data mapping."""
        return dict(self._data)
