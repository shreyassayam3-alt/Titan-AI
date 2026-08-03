"""Offline-capable research agent and its extensible provider architecture."""

from agents.research.agent import ResearchAgent
from agents.research.collector import NewsCollector
from agents.research.report_generator import ReportGenerator
from agents.research.source_manager import SourceManager

__all__ = ["NewsCollector", "ReportGenerator", "ResearchAgent", "SourceManager"]
