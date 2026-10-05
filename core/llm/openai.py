from __future__ import annotations

from typing import Any

from openai import OpenAI

from core.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str, *, base_url: str | None = None, default_model: str = "gpt-4o-mini") -> None:
        self._api_key = api_key
        self._default_model = default_model
        self._client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

    async def generate(self, prompt: str, *, system_prompt: str | None = None, model: str | None = None) -> str:
        responses_client = getattr(self._client, "responses")
        if callable(responses_client):
            responses_client = responses_client()

        response = responses_client.create(
            model=model or self._default_model,
            input=prompt,
            instructions=system_prompt,
        )

        output_text = getattr(response, "output_text", None)
        if output_text:
            return str(output_text)

        output = getattr(response, "output", None)
        if isinstance(output, list):
            pieces: list[str] = []
            for item in output:
                if isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        pieces.append(text)
                elif hasattr(item, "text"):
                    text = getattr(item, "text")
                    if isinstance(text, str):
                        pieces.append(text)
            if pieces:
                return "\n".join(pieces)

        if hasattr(response, "choices") and response.choices:
            first_choice = response.choices[0]
            message = getattr(first_choice, "message", None)
            if message is not None:
                content = getattr(message, "content", None)
                if isinstance(content, str):
                    return content
                if isinstance(content, list):
                    combined = []
                    for part in content:
                        if isinstance(part, dict):
                            value = part.get("text")
                            if isinstance(value, str):
                                combined.append(value)
                    if combined:
                        return "\n".join(combined)

        return str(response)
