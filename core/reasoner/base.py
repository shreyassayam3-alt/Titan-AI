"""Abstract contract for strategic reasoning components."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any


class Reasoner(ABC):
    """Evaluates alternatives and selects strategies without executing work.

    Implementations own their evaluation model and decision criteria. Callers
    need only provide alternatives and any context required for a decision.
    """

    @abstractmethod
    async def evaluate_options(
        self, options: Sequence[Any], *, context: Any | None = None
    ) -> Sequence[Any]:
        """Return evaluations for the supplied ``options``."""
        ...

    @abstractmethod
    async def select_strategy(
        self, options: Sequence[Any], *, context: Any | None = None
    ) -> Any:
        """Select and return the most suitable strategy from ``options``."""
        ...
