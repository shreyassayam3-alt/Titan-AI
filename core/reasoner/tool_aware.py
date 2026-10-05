from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from core.reasoner.base import Reasoner
from core.tools.base import ToolRegistry


class ToolAwareReasoner(Reasoner):
    """Reasons over options and chooses whether to invoke a tool before continuing."""

    def __init__(self, tool_registry: ToolRegistry | None = None) -> None:
        self._tool_registry = tool_registry

    async def evaluate_options(self, options: Sequence[Any], *, context: Any | None = None) -> Sequence[Any]:
        return tuple(options)

    async def select_strategy(self, options: Sequence[Any], *, context: Any | None = None) -> Any:
        if not self._tool_registry:
            return options[0] if options else None
        goal = str(context.get("goal", "") if isinstance(context, dict) else context or "")
        if any(keyword in goal.lower() for keyword in ("calculate", "read", "write", "execute", "browser", "file", "python")):
            discovered = await self._tool_registry.discover(query=goal)
            if discovered:
                suggestions = [tool.name for tool in discovered[:3]]
                return f"tool:{','.join(suggestions)}"
        return options[0] if options else None
