from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Any

from core.llm.env import load_dotenv


class LLMProvider(ABC):
    """Abstract interface for LLM-backed text generation."""

    name: str = ""

    @abstractmethod
    async def generate(self, prompt: str, *, system_prompt: str | None = None, model: str | None = None) -> str:
        """Generate a text response for the supplied prompt."""
        ...


class LLMProviderRegistry:
    """Create and select LLM providers from environment configuration."""

    def __init__(self, providers: list[LLMProvider] | None = None) -> None:
        self._providers = providers or []

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "LLMProviderRegistry":
        load_dotenv()
        env_map = env if env is not None else os.environ
        providers: list[LLMProvider] = []
        if env_map.get("OPENAI_API_KEY"):
            from core.llm.openai import OpenAIProvider
            providers.append(OpenAIProvider(api_key=env_map["OPENAI_API_KEY"]))
        if env_map.get("ANTHROPIC_API_KEY"):
            from core.llm.anthropic import AnthropicProvider
            providers.append(AnthropicProvider(api_key=env_map["ANTHROPIC_API_KEY"]))
        if env_map.get("GEMINI_API_KEY"):
            from core.llm.gemini import GeminiProvider
            providers.append(GeminiProvider(api_key=env_map["GEMINI_API_KEY"]))
        if env_map.get("OPENROUTER_API_KEY"):
            from core.llm.openrouter import OpenRouterProvider
            providers.append(OpenRouterProvider(api_key=env_map["OPENROUTER_API_KEY"]))
        if not providers:
            from core.llm.mock import MockLLMProvider
            providers.append(MockLLMProvider())
        return cls(providers)

    def get_provider(self) -> LLMProvider | None:
        return self._providers[0] if self._providers else None
