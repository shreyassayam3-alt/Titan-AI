"""Minimal concrete brain implementation for local orchestration."""

from typing import Any

from core.brain.base import Brain


class SimpleBrain(Brain):
    """A deterministic brain that returns the supplied input unchanged.

    It provides a concrete, dependency-free implementation while more capable
    reasoning backends are introduced in later layers.
    """

    async def think(self, input_data: Any, *, context: Any | None = None) -> Any:
        """Return ``input_data`` without contacting an external service."""
        return input_data
