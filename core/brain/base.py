"""Abstract contract for AI reasoning components."""

from abc import ABC, abstractmethod
from typing import Any


class Brain(ABC):
    """Produces a response from an input and optional execution context.

    Implementations may represent an LLM, a rules engine, or another reasoning
    system. This interface imposes no assumptions about transport or storage.
    """

    @abstractmethod
    async def think(self, input_data: Any, *, context: Any | None = None) -> Any:
        """Return the reasoning result for ``input_data``."""
        ...
