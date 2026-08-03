"""Abstract contracts for pluggable research data providers."""

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any

from agents.research.models import NewsItem, Source


class NewsProvider(ABC):
    """Supplies provider-neutral news items for a research topic."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider's stable registration name."""
        ...

    @abstractmethod
    async def get_news(self, topic: str) -> Sequence[NewsItem]:
        """Return news items relevant to ``topic``."""
        ...


class SearchProvider(ABC):
    """Supplies source references for a free-text query."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider's stable registration name."""
        ...

    @abstractmethod
    async def search(self, query: str) -> Sequence[Source]:
        """Return sources relevant to ``query``."""
        ...


class MarketProvider(ABC):
    """Supplies provider-neutral market data when a caller explicitly requests it."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider's stable registration name."""
        ...

    @abstractmethod
    async def get_market_data(self, identifier: str) -> Mapping[str, Any]:
        """Return a market-data snapshot for ``identifier``."""
        ...
