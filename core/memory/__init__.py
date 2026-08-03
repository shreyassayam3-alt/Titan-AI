"""Interfaces for stateful memory components."""

from core.memory.base import Memory
from core.memory.in_memory import InMemoryMemory

__all__ = ["InMemoryMemory", "Memory"]
