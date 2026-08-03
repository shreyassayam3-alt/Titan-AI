"""Abstract contracts for decision dimensions and strategy selection."""

from abc import ABC, abstractmethod
from typing import Any

from core.decision.models import DecisionContext


class StrategySelector(ABC):
    """Scores how well an action fits the desired execution strategy."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stable name used in policy inputs and diagnostics."""
        ...

    @abstractmethod
    async def evaluate(self, action: Any, context: DecisionContext) -> float:
        """Return a higher-is-better strategy score for ``action``."""
        ...


class RiskEvaluator(ABC):
    """Estimates risk associated with an action."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stable name used in policy inputs and diagnostics."""
        ...

    @abstractmethod
    async def evaluate(self, action: Any, context: DecisionContext) -> float:
        """Return a risk score for ``action``; lower values represent less risk."""
        ...


class CostEvaluator(ABC):
    """Estimates the cost of an action."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stable name used in policy inputs and diagnostics."""
        ...

    @abstractmethod
    async def evaluate(self, action: Any, context: DecisionContext) -> float:
        """Return a cost score for ``action``; lower values represent less cost."""
        ...


class ApprovalEvaluator(ABC):
    """Determines whether an action is eligible for automated selection."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the stable name used in policy inputs and diagnostics."""
        ...

    @abstractmethod
    async def evaluate(self, action: Any, context: DecisionContext) -> bool:
        """Return whether ``action`` satisfies the applicable approval policy."""
        ...
