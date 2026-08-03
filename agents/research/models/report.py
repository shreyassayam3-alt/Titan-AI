"""Research report model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from agents.research.models.news import NewsItem
from agents.research.models.source import Source


@dataclass(frozen=True, slots=True)
class ResearchReport:
    """An immutable report assembled from provider-neutral research material."""

    topic: str
    news_items: tuple[NewsItem, ...]
    sources: tuple[Source, ...]
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)
