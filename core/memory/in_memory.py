"""In-memory implementation of the memory contract."""

from typing import Any

from core.memory.base import Memory


class InMemoryMemory(Memory):
    """Stores values in process memory for a single runtime instance.

    This implementation is intended for local development and tests; its data
    is not shared across processes or retained after the instance is discarded.
    """

    def __init__(self) -> None:
        """Create an empty memory store."""
        self._values: dict[str, Any] = {}

    async def store(self, key: str, value: Any) -> None:
        """Store ``value`` under ``key`` in this process."""
        self._values[key] = value

    async def retrieve(self, key: str) -> Any | None:
        """Return the value for ``key``, or ``None`` when it is absent."""
        return self._values.get(key)

    async def delete(self, key: str) -> None:
        """Remove ``key`` when present."""
        self._values.pop(key, None)
