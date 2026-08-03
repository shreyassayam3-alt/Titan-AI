"""News collection service for the research agent."""

from agents.research.models import NewsItem
from agents.research.source_manager import SourceManager


class NewsCollector:
    """Collects news while remaining independent of concrete providers."""

    def __init__(self, source_manager: SourceManager) -> None:
        """Initialize the collector with the provider registry it queries."""
        self._source_manager = source_manager

    async def collect(self, topic: str) -> tuple[NewsItem, ...]:
        """Collect all currently available news items for ``topic``."""
        return await self._source_manager.collect_news(topic)
