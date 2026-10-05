"""Provider contracts and offline mock implementations."""

from agents.research.providers.adapters import GitHubProviderAdapter, LocalDocumentProviderAdapter, RSSProviderAdapter
from agents.research.providers.base import MarketProvider, NewsProvider, SearchProvider
from agents.research.providers.live import BraveSearchProvider, SerperSearchProvider, TavilySearchProvider
from agents.research.providers.mock import MockMarketProvider, MockNewsProvider, MockSearchProvider
from agents.research.providers.registry import ProviderQueryResponse, ProviderQueryResult, ProviderRegistry

__all__ = [
    "BraveSearchProvider",
    "GitHubProviderAdapter",
    "LocalDocumentProviderAdapter",
    "MarketProvider",
    "MockMarketProvider",
    "MockNewsProvider",
    "MockSearchProvider",
    "NewsProvider",
    "ProviderQueryResponse",
    "ProviderQueryResult",
    "ProviderRegistry",
    "RSSProviderAdapter",
    "SearchProvider",
    "SerperSearchProvider",
    "TavilySearchProvider",
]
