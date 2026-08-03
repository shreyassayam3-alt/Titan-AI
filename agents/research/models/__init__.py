"""Typed data models exchanged by research components."""

from agents.research.models.news import NewsItem
from agents.research.models.report import ResearchReport
from agents.research.models.source import Source

__all__ = ["NewsItem", "ResearchReport", "Source"]
