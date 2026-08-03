"""Abstract contract for workflow orchestration."""

from abc import ABC, abstractmethod
from typing import Any


class Orchestrator(ABC):
    """Coordinates execution of a request within an optional context."""

    @abstractmethod
    async def execute(self, request: Any, *, context: Any | None = None) -> Any:
        """Execute ``request`` and return its implementation-defined result."""
        ...
