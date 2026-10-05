from __future__ import annotations

from core.llm.base import LLMProvider


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def generate(self, prompt: str, *, system_prompt: str | None = None, model: str | None = None) -> str:
        return f"Anthropic response for: {prompt[:120]}"
