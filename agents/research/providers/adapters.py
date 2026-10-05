from __future__ import annotations

from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET
import re

from agents.research.models import NewsItem, Source
from agents.research.providers.base import NewsProvider, SearchProvider


class LocalDocumentProviderAdapter(SearchProvider, NewsProvider):
    """Indexes local markdown/text files as searchable knowledge sources."""

    def __init__(self, root: Path | str) -> None:
        self._root = Path(root)
        self._name = "local-documents"

    @property
    def name(self) -> str:
        return self._name

    async def search(self, query: str) -> list[Source]:
        matches = []
        for path in self._root.rglob("*.md"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if query.lower() in text.lower():
                matches.append(
                    Source(
                        name=f"Local doc: {path.name}",
                        url=str(path),
                        provider_name=self.name,
                    )
                )
        return matches[:5]

    async def get_news(self, topic: str) -> list[NewsItem]:
        items = []
        for path in self._root.rglob("*.md"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if topic.lower() in text.lower():
                items.append(
                    NewsItem(
                        headline=f"Local match: {path.name}",
                        source=Source(name=f"Local doc: {path.name}", url=str(path), provider_name=self.name),
                        summary=f"Referenced in {path}",
                    )
                )
        return items[:3]


class RSSProviderAdapter(NewsProvider, SearchProvider):
    """Parses a simple RSS/Atom feed into normalized items and sources."""

    def __init__(self, feed_path: Path | str) -> None:
        self._feed_path = Path(feed_path)
        self._name = "rss"

    @property
    def name(self) -> str:
        return self._name

    async def search(self, query: str) -> list[Source]:
        if not self._feed_path.exists():
            return []
        root = ET.parse(self._feed_path).getroot()
        sources = []
        for item in root.findall(".//item"):
            title = item.findtext("title") or ""
            description = item.findtext("description") or ""
            if query.lower() in (title + description).lower():
                sources.append(
                    Source(
                        name=title or "RSS item",
                        url=item.findtext("link"),
                        provider_name=self.name,
                    )
                )
        return sources[:5]

    async def get_news(self, topic: str) -> list[NewsItem]:
        if not self._feed_path.exists():
            return []
        root = ET.parse(self._feed_path).getroot()
        items = []
        for item in root.findall(".//item"):
            title = item.findtext("title") or ""
            description = item.findtext("description") or ""
            if topic.lower() in (title + description).lower():
                items.append(
                    NewsItem(
                        headline=title,
                        source=Source(name=title, url=item.findtext("link"), provider_name=self.name),
                        summary=description,
                    )
                )
        return items[:5]


class GitHubProviderAdapter(SearchProvider, NewsProvider):
    """Uses local repository metadata as a lightweight GitHub-style provider."""

    def __init__(self, repo_root: Path | str) -> None:
        self._repo_root = Path(repo_root)
        self._name = "github"

    @property
    def name(self) -> str:
        return self._name

    async def search(self, query: str) -> list[Source]:
        matches = []
        for path in self._repo_root.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if query.lower() in text.lower():
                matches.append(
                    Source(
                        name=f"GitHub file: {path.relative_to(self._repo_root)}",
                        url=str(path),
                        provider_name=self.name,
                    )
                )
        return matches[:5]

    async def get_news(self, topic: str) -> list[NewsItem]:
        items = []
        for path in self._repo_root.rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if topic.lower() in text.lower():
                items.append(
                    NewsItem(
                        headline=f"Repository reference: {path.name}",
                        source=Source(name=path.name, url=str(path), provider_name=self.name),
                        summary=f"Found in {path.relative_to(self._repo_root)}",
                    )
                )
        return items[:3]
