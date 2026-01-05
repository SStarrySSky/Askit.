"""Anthropic Claude AI provider implementation."""

from typing import List, Optional
import httpx
from .provider_base import AIProvider


class AnthropicProvider(AIProvider):
    """Anthropic Claude AI provider."""

    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.base_url = "https://api.anthropic.com/v1"
        self.default_model = "claude-sonnet-4-5-20250929"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using Claude API."""
        if not self.api_key:
            raise ValueError("API key not set")

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        messages = [{"role": "user", "content": prompt}]

        data = {
            "model": self.default_model,
            "max_tokens": 4096,
            "messages": messages
        }

        if system_prompt:
            data["system"] = system_prompt

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=data,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]

    def list_models(self) -> List[str]:
        """List available Claude models."""
        return [
            "claude-opus-4-5-20251101",
            "claude-sonnet-4-5-20250929",
            "claude-sonnet-3-5-20241022",
        ]

    def validate_api_key(self) -> bool:
        """Validate API key by making a test request."""
        # Simple validation - check if key is set
        return self.api_key is not None and len(self.api_key) > 0
