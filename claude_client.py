"""Small client for calling Anthropic's Claude Messages API."""

from __future__ import annotations

import os
from typing import Any

from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()


class ClaudeClient:
    """Create Claude messages using an API key from the environment."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        resolved_api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not resolved_api_key:
            raise ValueError(
                "Set ANTHROPIC_API_KEY in the environment before creating ClaudeClient."
            )

        self._client = Anthropic(api_key=resolved_api_key)
        self.model = model or os.getenv(
            "CLAUDE_MODEL", "claude-sonnet-4-20250514"
        )

    def ask(
        self,
        prompt: str,
        *,
        max_tokens: int = 1024,
        system: str | None = None,
        temperature: float | None = None,
    ) -> str:
        """Send one user prompt and return Claude's combined text response."""
        if not prompt.strip():
            raise ValueError("prompt must not be empty")
        if max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")

        request: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system is not None:
            request["system"] = system
        if temperature is not None:
            request["temperature"] = temperature

        response = self._client.messages.create(**request)
        return "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )


def ask_claude(
    prompt: str,
    *,
    max_tokens: int = 1024,
    system: str | None = None,
    temperature: float | None = None,
    model: str | None = None,
) -> str:
    """Convenience function for a single Claude request."""
    return ClaudeClient(model=model).ask(
        prompt,
        max_tokens=max_tokens,
        system=system,
        temperature=temperature,
    )
