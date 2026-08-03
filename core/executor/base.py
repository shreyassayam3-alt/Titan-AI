"""Abstract contract for task execution components."""

from abc import ABC, abstractmethod
from typing import Any


class Executor(ABC):
    """Executes tasks that have already passed the caller's validation policy."""

    @abstractmethod
    async def execute(self, validated_task: Any, *, context: Any | None = None) -> Any:
        """Execute ``validated_task`` and return its implementation-defined result."""
        ...
