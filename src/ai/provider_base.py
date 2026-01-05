"""Abstract base class for AI providers.

This module defines the interface that all AI providers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI provider.

        Args:
            api_key: API key for the provider
        """
        self.api_key = api_key

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a response from the AI.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            AI response text
        """
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available models.

        Returns:
            List of model names
        """
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """
        Validate the API key.

        Returns:
            True if valid, False otherwise
        """
        pass

    def get_name(self) -> str:
        """Get the provider name."""
        return self.__class__.__name__.replace("Provider", "")
