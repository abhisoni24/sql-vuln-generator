import os
from anthropic import Anthropic
from typing import Optional, List, Dict, Any


class ClaudeClient:
    """Claude/Anthropic client using the official Anthropic SDK.

    This uses the official Anthropic Python client library.
    The project places API keys in the .env file under CLAUDE_API_KEY.
    Supports prompt caching for improved efficiency with repeated system contexts.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-haiku-20241022"):
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY")
        self.model = model
        self.client = Anthropic(api_key=self.api_key)

    def send_prompt(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """Send a prompt to Claude and return the response."""
        if not self.api_key:
            raise RuntimeError("Claude API key not provided. Set CLAUDE_API_KEY in env.")

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            
            # Extract text from the response
            if message.content and len(message.content) > 0:
                content_block = message.content[0]
                # Check if it's a TextBlock with text attribute
                if hasattr(content_block, "text"):
                    return content_block.text.strip()  # type: ignore
            
            return ""
        except Exception as e:
            raise RuntimeError(f"Claude API error: {str(e)}")
    
    def send_prompt_with_system(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: int = 1024, 
        temperature: float = 0.0,
        cache_system: bool = False
    ) -> str:
        """Send a prompt with a system message, optionally cached.
        
        Args:
            system_prompt: The system context/instructions
            user_prompt: The user's message
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            cache_system: If True, cache the system prompt for reuse (saves tokens)
            
        Returns:
            The response text from Claude
        """
        if not self.api_key:
            raise RuntimeError("Claude API key not provided. Set CLAUDE_API_KEY in env.")

        try:
            # Build system message with optional caching
            system_content: Any = {
                "type": "text",
                "text": system_prompt
            }
            
            # Add cache control if requested (requires system prompt > 1024 tokens)
            if cache_system:
                system_content["cache_control"] = {"type": "ephemeral"}
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=[system_content],
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
            )
            
            # Extract text from the response
            if message.content and len(message.content) > 0:
                content_block = message.content[0]
                if hasattr(content_block, "text"):
                    return content_block.text.strip()  # type: ignore
            
            return ""
        except Exception as e:
            raise RuntimeError(f"Claude API error: {str(e)}")

    def get_sql_code(self, prompt: str, max_tokens: int = 1024) -> str:
        """Convenience wrapper that returns the raw completion text."""
        return self.send_prompt(prompt, max_tokens=max_tokens)