"""Minimal concrete brain implementation for local orchestration."""

from __future__ import annotations

from typing import Any

from core.brain.base import Brain


class SimpleBrain(Brain):
    """A simple local brain that keeps a lightweight memory footprint.

    This is intentionally dependency-free and suitable for experimentation before
    a heavier reasoning backend or LLM adapter is introduced.
    """

    def __init__(self) -> None:
        """Initialize the in-memory reasoning state."""
        self._memory: dict[str, Any] = {}

    async def think(self, input_data: Any, *, context: Any | None = None) -> Any:
        """Return a structured local reasoning result for the given input."""
        if isinstance(context, dict):
            self._memory.update(context)

        if isinstance(input_data, str):
            normalized = input_data.strip()
            return {
                "input": normalized,
                "memory_size": len(self._memory),
                "context": dict(context) if isinstance(context, dict) else context,
                "summary": normalized or "No input provided",
            }

        return {
            "input": input_data,
            "memory_size": len(self._memory),
            "context": dict(context) if isinstance(context, dict) else context,
        }
