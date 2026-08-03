"""Provider implementations for mission-runner research tasks."""

from __future__ import annotations

import re
from collections.abc import Sequence

from agents.research.models import NewsItem, Source
from agents.research.providers.base import NewsProvider, SearchProvider


class KeywordSearchProvider(SearchProvider):
    """Generates multiple source candidates from a natural-language query."""

    name = "keyword-search"

    async def search(self, query: str) -> Sequence[Source]:
        tokens = self._tokens(query)
        topic = " ".join(tokens[:4]) or query.strip()
        title = topic.title()
        return (
            Source(name=f"{title} Overview", url=f"https://example.test/{self._slug(topic)}/overview", provider_name=self.name),
            Source(name=f"{title} Briefing", url=f"https://example.test/{self._slug(topic)}/briefing", provider_name=self.name),
            Source(name=f"{title} Digest", url=f"https://example.test/{self._slug(topic)}/digest", provider_name=self.name),
        )

    @staticmethod
    def _tokens(query: str) -> list[str]:
        return [token for token in re.findall(r"[a-z0-9]+", query.lower()) if len(token) > 2]

    @staticmethod
    def _slug(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


class KeywordNewsProvider(NewsProvider):
    """Produces news-like items for a research topic without external dependencies."""

    name = "keyword-news"

    async def get_news(self, topic: str) -> Sequence[NewsItem]:
        topic_title = topic.strip() or "research topic"
        return (
            NewsItem(
                headline=f"{topic_title}: emerging signals",
                source=Source(name=f"{topic_title} Signals", url=f"https://example.test/{self._slug(topic_title)}/signals", provider_name=self.name),
                summary="Multiple updates point to growing momentum around the topic.",
            ),
            NewsItem(
                headline=f"{topic_title}: key stakeholders",
                source=Source(name=f"{topic_title} Stakeholders", url=f"https://example.test/{self._slug(topic_title)}/stakeholders", provider_name=self.name),
                summary="Analysts and operators are concentrating attention on the same themes.",
            ),
            NewsItem(
                headline=f"{topic_title}: open questions",
                source=Source(name=f"{topic_title} Questions", url=f"https://example.test/{self._slug(topic_title)}/questions", provider_name=self.name),
                summary="The current evidence still leaves several important questions unresolved.",
            ),
        )

    @staticmethod
    def _slug(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", value).strip("-")
