"""OpenAI-compatible AI provider.

This provider supports OpenAI API and any OpenAI-compatible services
(like Ollama, LocalAI, etc.) through custom base URLs.
"""

from typing import Optional, List
import httpx
from loguru import logger
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .provider_base import AIProvider

# Thread pool for sync HTTP requests
_executor = ThreadPoolExecutor(max_workers=2)


class OpenAIProvider(AIProvider):
    """OpenAI-compatible AI provider with custom base URL support."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        model: str = "gpt-4",
        timeout: float = 60.0
    ):
        """Initialize OpenAI provider."""
        self.api_key = api_key
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip('/')
        self.model = model
        self.timeout = timeout
        logger.info(f"Initialized OpenAI provider with base_url: {self.base_url}")

    def _is_reasoning_model(self, model: str) -> bool:
        """
        Detect if a model is a reasoning/completion model.

        Args:
            model: Model name

        Returns:
            True if reasoning model, False if chat model
        """
        reasoning_keywords = [
            "think", "reasoning", "r1", "o1", "o3",
            "deepseek-v3.1-think", "deepseek-reasoner"
        ]
        model_lower = model.lower()
        return any(keyword in model_lower for keyword in reasoning_keywords)

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate response using sync HTTP in thread pool."""
        model = kwargs.get("model", self.model)
        is_reasoning = self._is_reasoning_model(model)
        stream_callback = kwargs.get("stream_callback", None)

        # Run sync request in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _executor,
            self._generate_sync,
            prompt, model, is_reasoning, stream_callback, kwargs
        )

    def _generate_sync(self, prompt, model, is_reasoning, stream_callback, kwargs) -> str:
        """Synchronous generate implementation."""
        import json

        url = f"{self.base_url}/{'completions' if is_reasoning else 'chat/completions'}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        if is_reasoning:
            payload = {
                "model": model,
                "prompt": prompt,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000),
                "stream": stream_callback is not None
            }
        else:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000),
                "stream": stream_callback is not None
            }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                if payload["stream"]:
                    return self._stream_response(client, url, headers, payload, is_reasoning, stream_callback)
                else:
                    response = client.post(url, json=payload, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                    content = data["choices"][0]["text" if is_reasoning else "message"]["content"] if not is_reasoning else data["choices"][0]["text"]
                    if not is_reasoning:
                        content = data["choices"][0]["message"]["content"]
                    logger.info(f"Received response ({len(content)} chars)")
                    return content
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code}")
            raise Exception(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise

    def _stream_response(self, client, url, headers, payload, is_reasoning, stream_callback) -> str:
        """Handle streaming response synchronously."""
        import json
        full_content = ""

        with client.stream("POST", url, json=payload, headers=headers) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line or line.strip() == "":
                    continue
                if line.startswith("data: "):
                    line = line[6:]
                if line.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(line)
                    choices = chunk.get("choices", [])
                    if not choices:
                        continue
                    if is_reasoning:
                        delta = choices[0].get("text", "")
                    else:
                        delta = choices[0].get("delta", {}).get("content", "")
                    if delta:
                        full_content += delta
                        if stream_callback:
                            stream_callback(delta, len(full_content))
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue

        logger.info(f"Received streamed response ({len(full_content)} chars)")
        return full_content

    async def list_models(self) -> List[str]:
        """List available models from the API."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._list_models_sync)

    def _list_models_sync(self) -> List[str]:
        """Synchronous list models implementation."""
        url = f"{self.base_url}/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                models = [m["id"] for m in data.get("data", [])]
                logger.info(f"Found {len(models)} models")
                return models
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []

    def validate_api_key(self) -> bool:
        """Validate the API key."""
        try:
            models = self._list_models_sync()
            return len(models) > 0
        except Exception as e:
            logger.error(f"API key validation failed: {e}")
            return False
