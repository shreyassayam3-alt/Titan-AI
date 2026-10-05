from __future__ import annotations

import os
from typing import Any

from core.llm.env import load_dotenv


class LLMConfigurationError(ValueError):
    """Raised when no usable LLM API key is available."""


def validate_llm_keys(env: dict[str, str] | None = None) -> dict[str, str]:
    load_dotenv()
    env_map = env if env is not None else os.environ
    available = {
        key: value
        for key, value in {
            "OPENAI_API_KEY": env_map.get("OPENAI_API_KEY", ""),
            "ANTHROPIC_API_KEY": env_map.get("ANTHROPIC_API_KEY", ""),
            "GEMINI_API_KEY": env_map.get("GEMINI_API_KEY", ""),
            "OPENROUTER_API_KEY": env_map.get("OPENROUTER_API_KEY", ""),
        }.items()
        if value
    }
    if not available:
        raise LLMConfigurationError("No LLM API key found in .env or environment variables.")
    return available
