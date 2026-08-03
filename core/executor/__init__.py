"""Interfaces for executing validated task units."""

from core.executor.base import Executor
from core.executor.placeholder import PlaceholderExecutor

__all__ = ["Executor", "PlaceholderExecutor"]
