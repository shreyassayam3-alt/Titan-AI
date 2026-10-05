"""Weighted strategy selection for decision optimization."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from core.reasoner.base import Reasoner


class WeightedReasoner(Reasoner):
    """Evaluates options using weighted scoring criteria."""

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        """Initialize with optional weighting scheme."""
        self._weights = weights or {"priority": 1.0, "complexity": 0.5}

    async def evaluate_options(
        self, options: Sequence[Any], *, context: Any | None = None
    ) -> Sequence[Any]:
        """Score each option based on available attributes."""
        scored = []
        for option in options:
            score = self._compute_score(option, context)
            scored.append((option, score))
        return tuple(opt for opt, _ in sorted(scored, key=lambda x: x[1], reverse=True))

    async def select_strategy(
        self, options: Sequence[Any], *, context: Any | None = None
    ) -> Any:
        """Return the highest-scoring option."""
        evaluated = await self.evaluate_options(options, context=context)
        return evaluated[0] if evaluated else None

    def _compute_score(self, option: Any, context: Any | None) -> float:
        """Compute weighted score for an option."""
        score = 0.0

        # Favor higher priority
        if hasattr(option, "priority"):
            score += float(option.priority) * self._weights.get("priority", 1.0)

        # Penalize complexity
        if hasattr(option, "complexity"):
            score -= float(option.complexity) * self._weights.get("complexity", 0.5)

        return score
