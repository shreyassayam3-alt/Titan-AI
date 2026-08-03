"""Policy contracts and generic weighted policy implementation."""

from abc import ABC, abstractmethod
from collections.abc import Mapping


class DecisionPolicy(ABC):
    """Combines evaluator outputs into comparable action scores."""

    @abstractmethod
    def score(self, evaluations: Mapping[str, float | bool]) -> float:
        """Return a higher-is-better score from named evaluator outputs."""
        ...


class WeightedDecisionPolicy(DecisionPolicy):
    """Combines numeric evaluator values using caller-configured weights.

    Negative weights naturally model dimensions such as risk and cost without
    embedding any domain-specific assumptions in the engine.
    """

    def __init__(self, weights: Mapping[str, float]) -> None:
        """Store the weights applied to matching numeric evaluator names."""
        self._weights = dict(weights)

    def score(self, evaluations: Mapping[str, float | bool]) -> float:
        """Return the weighted sum of the policy's numeric evaluation inputs."""
        return sum(
            self._weights.get(name, 0.0) * float(value)
            for name, value in evaluations.items()
            if isinstance(value, (float, int)) and not isinstance(value, bool)
        )
