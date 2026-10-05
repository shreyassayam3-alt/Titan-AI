from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from agents.research.providers.base import NewsProvider, SearchProvider


@dataclass(slots=True)
class ProviderQueryResult:
    """Normalized result returned by a provider after a query."""

    provider_name: str
    title: str
    content: str
    url: str | None = None
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderQueryResponse:
    """Merged response from multiple providers."""

    query: str
    results: list[ProviderQueryResult] = field(default_factory=list)
    providers_used: list[str] = field(default_factory=list)
    summary: str = ""


class ProviderRegistry:
    """Routes queries to multiple provider adapters and normalizes the output."""

    def __init__(self) -> None:
        self._providers: list[object] = []

    def register(self, provider: object) -> None:
        if not isinstance(provider, (NewsProvider, SearchProvider)):
            raise TypeError("Provider must implement the supported research provider interfaces")
        self._providers.append(provider)

    async def query(self, query: str) -> ProviderQueryResponse:
        tasks: list[asyncio.Task[list[ProviderQueryResult]]] = []
        for provider in self._providers:
            if isinstance(provider, SearchProvider):
                tasks.append(asyncio.create_task(self._collect_search(provider, query)))
            if isinstance(provider, NewsProvider):
                tasks.append(asyncio.create_task(self._collect_news(provider, query)))

        batches = await asyncio.gather(*tasks) if tasks else []
        results = [item for batch in batches for item in batch]
        providers_used = [provider.name for provider in self._providers]

        deduped = self._deduplicate(results)
        ranked = sorted(deduped, key=lambda item: item.confidence, reverse=True)
        summary = self._summarize(ranked, query)
        return ProviderQueryResponse(
            query=query,
            results=ranked,
            providers_used=list(dict.fromkeys(providers_used)),
            summary=summary,
        )

    async def _collect_search(self, provider: SearchProvider, query: str) -> list[ProviderQueryResult]:
        items: list[ProviderQueryResult] = []
        for source in await provider.search(query):
            items.append(
                ProviderQueryResult(
                    provider_name=provider.name,
                    title=source.name,
                    content=source.url or "",
                    url=source.url,
                    confidence=self._confidence(provider.name, source.name, query),
                    metadata={"source_id": source.id},
                )
            )
        return items

    async def _collect_news(self, provider: NewsProvider, query: str) -> list[ProviderQueryResult]:
        items: list[ProviderQueryResult] = []
        for news_item in await provider.get_news(query):
            items.append(
                ProviderQueryResult(
                    provider_name=provider.name,
                    title=news_item.headline,
                    content=news_item.summary or news_item.headline,
                    url=news_item.source.url,
                    confidence=self._confidence(provider.name, news_item.headline, query),
                    metadata={"news_id": news_item.id},
                )
            )
        return items

    @staticmethod
    def _deduplicate(results: Sequence[ProviderQueryResult]) -> list[ProviderQueryResult]:
        seen: set[tuple[str, str]] = set()
        deduped: list[ProviderQueryResult] = []
        for result in results:
            key = (result.provider_name, result.title.lower())
            if key in seen:
                continue
            seen.add(key)
            deduped.append(result)
        return deduped

    @staticmethod
    def _confidence(provider_name: str, title: str, query: str) -> float:
        score = 0.3
        if provider_name:
            score += 0.2
        if query.lower() in title.lower():
            score += 0.3
        return round(min(score + 0.1 * len(title.split()), 1.0), 2)

    @staticmethod
    def _summarize(results: Sequence[ProviderQueryResult], query: str) -> str:
        if not results:
            return f"No providers returned results for '{query}'."
        top = results[0]
        return f"{len(results)} normalized results for '{query}' ranked from {top.provider_name}."
