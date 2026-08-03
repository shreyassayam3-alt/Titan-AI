"""Abstract contract for storing and retrieving agent state."""

from abc import ABC, abstractmethod
from typing import Any


class Memory(ABC):
    """Persists values under implementation-defined keys and retrieval rules."""

    @abstractmethod
    async def store(self, key: str, value: Any) -> None:
        """Store ``value`` under ``key``."""
        ...

    @abstractmethod
    async def retrieve(self, key: str) -> Any | None:
        """Return the value associated with ``key``, if one exists."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove the value associated with ``key`` if supported."""
        ...
