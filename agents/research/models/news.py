"""News item model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from agents.research.models.source import Source


@dataclass(frozen=True, slots=True)
class NewsItem:
    """A provider-neutral news item collected during research."""

    headline: str
    source: Source
    summary: str = ""
    published_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
