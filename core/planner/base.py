"""Abstract contract for task planning components."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any


class Planner(ABC):
    """Transforms goals into plans and independently executable task units."""

    @abstractmethod
    async def create_plan(self, goal: Any, *, context: Any | None = None) -> Any:
        """Create and return a plan for ``goal`` using optional ``context``."""
        ...

    @abstractmethod
    async def decompose_goal(self, goal: Any, *, context: Any | None = None) -> Sequence[Any]:
        """Break ``goal`` into an ordered sequence of implementation-defined tasks."""
        ...
