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
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text or ""
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")

    def get_model_name(self) -> str:
        return self.model

    def get_provider_name(self) -> str:
        return "Google"

    # Legacy alias used elsewhere in project
    generate_sql = get_sql_code
