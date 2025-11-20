import os
from typing import Optional
try:
    from google import genai
except Exception:
    genai = None  # type: ignore

from .base_llm_client import BaseLLMClient
from dotenv import load_dotenv

load_dotenv()


class GeminiClient(BaseLLMClient):
    """Client wrapper for Google's Generative API (Gemini) using the
    `google-genai` client library.

    This client uses the `genai.Client` interface as demonstrated in `test_api.py`.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3-pro"):
        # Support either GEMINI_API_KEY or GOOGLE_API_KEY env var names
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise RuntimeError("Google/Gemini API key not provided. Set GEMINI_API_KEY or GOOGLE_API_KEY in env.")

        if genai is None:
            raise RuntimeError("google-genai (genai) library not available in this environment")

        # Create a client instance (matches pattern in test_api.py)
        self.client = genai.Client(api_key=self.api_key)
        self.model = model

    def get_sql_code(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """Generate SQL/code using the Gemini model via the genai client.

        Uses `client.models.generate_content` to generate content and returns the text response.
        """
        try:
            config = genai.types.GenerateContentConfig(
                temperature=temperature
                # Note: max_output_tokens removed as it can cause issues with short responses
            )
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            return response.text or ""
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "Google"

    def send_prompt(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """Send a prompt to Gemini and return the response."""
        try:
            config = genai.types.GenerateContentConfig(
                temperature=temperature
                # Note: max_output_tokens removed as it can cause issues with short responses
            )
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            return response.text or ""
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")
    
    def send_prompt_with_system(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: int = 1024, 
        temperature: float = 0.0,
        cache_system: bool = False
    ) -> str:
        """Send a prompt with a system message to Gemini.
        
        Uses the system_instruction parameter in the config for proper system message handling.
        
        Args:
            system_prompt: The system context/instructions
            user_prompt: The user's message
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            cache_system: Ignored for Gemini (not supported)
            
        Returns:
            The response text from Gemini
        """
        try:
            config = genai.types.GenerateContentConfig(
                temperature=temperature,
                system_instruction=system_prompt
                # Note: max_output_tokens removed as it can cause issues with short responses
            )
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config
            )
            return response.text or ""
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")

    # Legacy alias used elsewhere in project
    generate_sql = get_sql_code
