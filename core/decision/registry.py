"""Registry for plugin-provided numeric action evaluators."""

from abc import ABC, abstractmethod
from typing import Any

from core.decision.models import DecisionContext


class DecisionEvaluator(ABC):
    """Generic numeric evaluator contract for decision plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stable evaluation dimension name."""
        ...

    @abstractmethod
    async def evaluate(self, action: Any, context: DecisionContext) -> float:
        """Return a numeric value for one action and decision context."""
        ...


class EvaluatorRegistry:
    """Stores independently registered evaluator plugins by unique name."""

    def __init__(self) -> None:
        """Create an empty evaluator plugin registry."""
        self._evaluators: dict[str, DecisionEvaluator] = {}

    def register(self, evaluator: DecisionEvaluator) -> None:
        """Register a plugin evaluator under its stable name."""
        if evaluator.name in self._evaluators:
            raise ValueError(f"An evaluator named '{evaluator.name}' is already registered.")
        self._evaluators[evaluator.name] = evaluator

    def evaluators(self) -> tuple[DecisionEvaluator, ...]:
        """Return registered evaluators in registration order."""
        return tuple(self._evaluators.values())
