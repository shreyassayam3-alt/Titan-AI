"""Abstract contract for learning from completed tasks."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any


class Learning(ABC):
    """Records completed work and exposes relevant prior experience.

    This contract does not prescribe how experiences are represented, persisted,
    scored, or used by a learning implementation.
    """

    @abstractmethod
    async def record_completed_task(self, task: Any, result: Any) -> None:
        """Record the completed ``task`` and its resulting outcome."""
        ...

    @abstractmethod
    async def retrieve_experience(
        self, query: Any, *, limit: int | None = None
    ) -> Sequence[Any]:
        """Return past experiences relevant to ``query``."""
        ...
