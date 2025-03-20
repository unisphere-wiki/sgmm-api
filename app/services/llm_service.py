"""
Service for interacting with Large Language Models (LLMs).
"""
import logging
import os
from typing import Dict, Any, Optional

import openai

class LLMService:
    """
    Service for generating text using LLMs.
    """
    
    def __init__(self) -> None:
        """Initialize the LLMService."""
        self.logger = logging.getLogger(__name__)
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.model = os.environ.get("LLM_MODEL", "gpt-4o")
        
        if not self.api_key:
            self.logger.warning("OPENAI_API_KEY environment variable not set")
    
    def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        Generate text using an LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated text
        """
        try:
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            openai.api_key = self.api_key
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            self.logger.error(f"Error generating text: {str(e)}")
            return f"Error generating text: {str(e)}" 