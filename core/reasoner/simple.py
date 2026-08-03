"""Minimal reasoner implementation for deterministic local workflows."""

from collections.abc import Sequence
from typing import Any

from core.reasoner.base import Reasoner


class SimpleReasoner(Reasoner):
    """Preserves provided options and selects their first available strategy."""

    async def evaluate_options(
        self, options: Sequence[Any], *, context: Any | None = None
    ) -> Sequence[Any]:
        """Return a tuple copy of ``options`` without applying a scoring model."""
        return tuple(options)

    async def select_strategy(
        self, options: Sequence[Any], *, context: Any | None = None
    ) -> Any:
        """Return the first option, or ``None`` when no options are available."""
        return options[0] if options else None
