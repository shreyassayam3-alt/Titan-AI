from __future__ import annotations

from core.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    """Fallback provider used when no real API keys are configured."""

    name = "mock"

    async def generate(self, prompt: str, *, system_prompt: str | None = None, model: str | None = None) -> str:
        return f"Mock summary for: {prompt[:120]}"
