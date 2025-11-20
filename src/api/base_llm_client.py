"""
Abstract base class for LLM clients to enable multiple provider support.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM clients.
    
    All LLM providers (OpenAI, Claude, Ollama, etc.) should implement this interface
    to ensure consistency across the experiment framework.
    """
    
    @abstractmethod
    def get_sql_code(
        self, 
        prompt: str, 
        max_tokens: int = 1024, 
        temperature: float = 0.0
    ) -> str:
        """
        Generate SQL code based on the provided prompt.
        
        Args:
            prompt: The prompt describing the code to generate
            max_tokens: Maximum number of tokens in the response
            temperature: Sampling temperature (0.0 = deterministic, higher = more creative)
            
        Returns:
            Generated SQL code as a string
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name/identifier of the model being used.
        
        Returns:
            Model name string (e.g., "gpt-3.5-turbo", "qwen3:8b", etc.)
        """
        pass
    
    @abstractmethod
    def send_prompt_with_system(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: int = 1024, 
        temperature: float = 0.0,
        cache_system: bool = False
    ) -> str:
        """
        Send a prompt with system context for analysis.
        
        Args:
            system_prompt: System context/instructions
            user_prompt: The user's message
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            cache_system: Whether to cache system prompt (implementation dependent)
            
        Returns:
            Response text from the LLM
        """
        pass
