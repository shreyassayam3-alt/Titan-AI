from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urlencode

from agents.research.models import NewsItem, Source
from agents.research.providers.base import NewsProvider, SearchProvider


class TavilySearchProvider(SearchProvider):
    """Live search adapter for the Tavily API."""

    name = "tavily"

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.getenv("TAVILY_API_KEY", "")

    async def search(self, query: str) -> list[Source]:
        if not self._api_key:
            return []
        payload = {"api_key": self._api_key, "query": query, "search_depth": "basic"}
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post("https://api.tavily.com/search", json=payload)
            response.raise_for_status()
            data = response.json()
        return [
            Source(
                name=item.get("title") or "Tavily result",
                url=item.get("url"),
                provider_name=self.name,
            )
            for item in data.get("results", [])
        ]


class BraveSearchProvider(SearchProvider):
    """Live search adapter for the Brave Search API."""

    name = "brave"

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.getenv("BRAVE_API_KEY", "")

    async def search(self, query: str) -> list[Source]:
        if not self._api_key:
            return []
        params = {"q": query, "count": 5}
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"X-Api-Key": self._api_key},
                params=params,
            )
            response.raise_for_status()
            data = response.json()
        return [
            Source(
                name=item.get("title") or "Brave result",
                url=item.get("url"),
                provider_name=self.name,
            )
            for item in data.get("web", {}).get("results", [])
        ]


class SerperSearchProvider(SearchProvider, NewsProvider):
    """Live search adapter for the Serper API."""

    name = "serper"

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.getenv("SERPER_API_KEY", "")

    async def search(self, query: str) -> list[Source]:
        if not self._api_key:
            return []
        payload = {"q": query}
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self._api_key, "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return [
            Source(
                name=item.get("title") or "Serper result",
                url=item.get("link"),
                provider_name=self.name,
            )
            for item in data.get("organic", [])
        ]

    async def get_news(self, topic: str) -> list[NewsItem]:
        if not self._api_key:
            return []
        payload = {"q": topic}
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://google.serper.dev/news",
                headers={"X-API-KEY": self._api_key, "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
        return [
            NewsItem(
                headline=item.get("title") or "Serper news item",
                source=Source(name=item.get("title") or "Serper news item", url=item.get("link"), provider_name=self.name),
                summary=item.get("snippet", ""),
            )
            for item in data.get("news", [])
        ]
