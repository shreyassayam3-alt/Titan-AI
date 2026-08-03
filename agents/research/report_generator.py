"""Report assembly service for collected research material."""

from collections.abc import Sequence

from agents.research.models import NewsItem, ResearchReport, Source


class ReportGenerator:
    """Builds provider-neutral reports without making acquisition decisions."""

    def generate(
        self,
        topic: str,
        news_items: Sequence[NewsItem],
        discovered_sources: Sequence[Source] = (),
    ) -> ResearchReport:
        """Create a report from supplied items and explicitly discovered sources."""
        sources_by_id = {source.id: source for source in discovered_sources}
        for item in news_items:
            sources_by_id.setdefault(item.source.id, item.source)
        return ResearchReport(
            topic=topic,
            news_items=tuple(news_items),
            sources=tuple(sources_by_id.values()),
        )
