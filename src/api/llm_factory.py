"""
Factory for creating LLM clients with unified interface.
"""

from typing import Optional
from .base_llm_client import BaseLLMClient
from .claude_client import ClaudeClient
from .gemini_client import GeminiClient
from .openai_client import OpenAIClient
from .ollama_client import OllamaClient


class LLMFactory:
    """Factory for creating LLM clients."""

    PROVIDERS = {
        'claude': ClaudeClient,
        'gemini': GeminiClient,
        'openai': OpenAIClient,
        'ollama': OllamaClient,
    }

    @staticmethod
    def create(provider: str, model: Optional[str] = None, **kwargs) -> BaseLLMClient:
        """
        Create an LLM client instance.

        Args:
            provider: The LLM provider ('claude', 'gemini', 'openai')
            model: The specific model to use (optional)
            **kwargs: Additional arguments for the client

        Returns:
            Configured LLM client instance

        Raises:
            ValueError: If provider is not supported
        """
        if provider not in LLMFactory.PROVIDERS:
            available = ', '.join(LLMFactory.PROVIDERS.keys())
            raise ValueError(f"Unsupported provider '{provider}'. Available: {available}")

        client_class = LLMFactory.PROVIDERS[provider]

        # Create client with model if specified
        if model:
            return client_class(model=model, **kwargs)
        else:
            return client_class(**kwargs)

    @staticmethod
    def get_available_providers() -> list:
        """Get list of available LLM providers."""
        return list(LLMFactory.PROVIDERS.keys())