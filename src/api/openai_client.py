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
        """Send a prompt to OpenAI and return the SQL code."""
        # Try newer API format first (max_completion_tokens), fall back to older format (max_tokens)
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception:
            # Fall back to older API format
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

    def send_prompt_with_system(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: int = 1024, 
        temperature: float = 0.0,
        cache_system: bool = False
    ) -> str:
        """Send a prompt with system message to OpenAI."""
        # Try newer API format first (max_completion_tokens), fall back to older format (max_tokens)
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception:
            # Fall back to older API format
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )
        
        if resp.choices and len(resp.choices) > 0:
            content = resp.choices[0].message.content
            return content.strip() if content else ""
        
        return ""

    # keep legacy names if other code expects them
    generate_sql = get_sql_code