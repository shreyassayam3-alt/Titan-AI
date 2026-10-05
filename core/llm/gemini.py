from __future__ import annotations

from core.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def generate(self, prompt: str, *, system_prompt: str | None = None, model: str | None = None) -> str:
        return f"Gemini response for: {prompt[:120]}"
