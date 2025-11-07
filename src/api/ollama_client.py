"""
Ollama client for running local LLMs (Qwen, Llama, Mistral, etc.)
"""

import os
import requests
from typing import Optional

from .base_llm_client import BaseLLMClient


class OllamaClient(BaseLLMClient):
    """
    Client for Ollama-based local LLM models.
    
    Supports models like Qwen, Llama, Mistral, etc. running locally via Ollama.
    Requires Ollama server to be running (ollama serve).
    Uses direct HTTP API to avoid streaming issues.
    """
    
    def __init__(
        self, 
        model: str = "qwen2.5-coder:7b",
        base_url: Optional[str] = None,
        context_window: int = 8192,
        temperature: float = 0.0
    ):
        """
        Initialize Ollama client.
        
        Args:
            model: Ollama model name (e.g., "qwen2.5-coder:7b", "qwen3:8b", "llama3.1:8b")
            base_url: Optional custom Ollama server URL (default: http://localhost:11434)
            context_window: Context window size for the model
            temperature: Default temperature for generation
        """
        self.model = model
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.context_window = context_window
        self.default_temperature = temperature
        
        print(f"✓ Initialized Ollama client: {model} (context: {context_window})")
    
    def get_sql_code(
        self, 
        prompt: str, 
        max_tokens: int = 1024, 
        temperature: float = 0.0
    ) -> str:
        """
        Generate SQL code using the local Ollama model via direct HTTP API.
        
        Args:
            prompt: The prompt describing the code to generate
            max_tokens: Maximum number of tokens in the response
            temperature: Sampling temperature
            
        Returns:
            Generated SQL code as a string
        """
        try:
            print(f"  → Sending request to Ollama ({self.model})...")
            print(f"     Prompt length: {len(prompt)} chars")
            
            # Use direct HTTP API with stream=false for reliability
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,  # Critical: disable streaming
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "num_ctx": self.context_window
                }
            }
            
            # Make request with generous timeout
            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            
            # Extract response
            result = response.json()
            generated_text = result.get("response", "")
            
            print(f"  ✓ Received response from Ollama ({len(generated_text)} chars)")
            
            return generated_text.strip() if generated_text else ""
            
        except requests.Timeout:
            print(f"  ✗ Timeout waiting for Ollama (180s)")
            return ""
        except requests.RequestException as e:
            print(f"  ✗ HTTP error: {e}")
            return ""
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def get_model_name(self) -> str:
        """Get the Ollama model name."""
        return self.model
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "Ollama"
    
    # Legacy compatibility
    generate_sql = get_sql_code


# Common Ollama model presets for easy initialization
class OllamaModels:
    """Predefined Ollama model configurations."""
    
    # Coding-focused models
    QWEN_CODER_7B = "qwen2.5-coder:7b"
    QWEN_CODER_14B = "qwen2.5-coder:14b"
    QWEN_CODER_32B = "qwen2.5-coder:32b"
    CODELLAMA_7B = "codellama:7b"
    CODELLAMA_13B = "codellama:13b"
    DEEPSEEK_CODER_6B = "deepseek-coder:6.7b"
    DEEPSEEK_CODER_33B = "deepseek-coder:33b"
    
    # General models
    QWEN_7B = "qwen2.5:7b"
    QWEN_14B = "qwen2.5:14b"
    LLAMA3_8B = "llama3.1:8b"
    LLAMA3_70B = "llama3.1:70b"
    MISTRAL_7B = "mistral:7b"
    
    @staticmethod
    def get_recommended_context_window(model: str) -> int:
        """Get recommended context window for a model."""
        context_windows = {
            "qwen2.5-coder:7b": 32768,
            "qwen2.5-coder:14b": 32768,
            "qwen2.5-coder:32b": 32768,
            "qwen2.5:7b": 32768,
            "qwen2.5:14b": 32768,
            "codellama:7b": 16384,
            "codellama:13b": 16384,
            "llama3.1:8b": 128000,
            "llama3.1:70b": 128000,
            "mistral:7b": 32768,
            "deepseek-coder:6.7b": 16384,
            "deepseek-coder:33b": 16384,
        }
        return context_windows.get(model, 8192)
