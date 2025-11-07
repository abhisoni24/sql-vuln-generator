import os
from openai import OpenAI
from typing import Optional

from .base_llm_client import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """Wrapper around OpenAI ChatCompletion API (gpt-3.5-turbo).

    Exposes `get_sql_code` to return assistant output for a prompt.
    Uses the modern OpenAI client library.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OpenAI API key not provided. Set OPENAI_API_KEY in env.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def get_sql_code(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """Send a prompt to GPT-3.5 and return the SQL code."""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        if resp.choices and len(resp.choices) > 0:
            content = resp.choices[0].message.content
            return content.strip() if content else ""
        
        return ""

    def get_model_name(self) -> str:
        """Get the OpenAI model name."""
        return self.model
    
    def get_provider_name(self) -> str:
        """Get the provider name."""
        return "OpenAI"

    # keep legacy names if other code expects them
    generate_sql = get_sql_code