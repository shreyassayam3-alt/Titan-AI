from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from core.llm.base import LLMProvider
from core.reasoner.base import Reasoner


class LLMReasoner(Reasoner):
    """Uses an LLM provider to evaluate options and pick a strategy."""

    def __init__(self, provider: LLMProvider | None = None) -> None:
        self._provider = provider

    async def evaluate_options(self, options: Sequence[Any], *, context: Any | None = None) -> Sequence[Any]:
        if not self._provider:
            return tuple(options)
        prompt = "Evaluate the following options for the mission: " + ", ".join(str(option) for option in options)
        await self._provider.generate(prompt, system_prompt="You are Titan's mission reasoner.")
        return tuple(options)

    async def select_strategy(self, options: Sequence[Any], *, context: Any | None = None) -> Any:
        if not self._provider:
            return options[0] if options else None
        prompt = str(options[0]) if options else ""
        response = await self._provider.generate(prompt, system_prompt="You are Titan's mission reasoner.")
        return response or (options[0] if options else None)
