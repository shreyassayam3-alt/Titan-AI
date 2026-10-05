from __future__ import annotations

from core.llm.base import LLMProvider


class OpenRouterProvider(LLMProvider):
    name = "openrouter"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def generate(self, prompt: str, *, system_prompt: str | None = None, model: str | None = None) -> str:
        return f"OpenRouter response for: {prompt[:120]}"
